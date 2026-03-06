# Graph Admin Studio (GAS) — Windows Runner Quick Install (v0)
#
# This script is intended to be downloaded from the control plane host:
#   iwr $env:CONTROL_PLANE_URL/install/windows.ps1 -UseBasicParsing | iex
#
# Inputs (env or params):
#   CONTROL_PLANE_URL  - required
#   GAS_PAIRING_CODE   - required when CONTROL_PLANE_REQUIRE_PAIRING_CODE=true on server

[CmdletBinding()]
param(
  [string]$ControlPlaneUrl = $env:CONTROL_PLANE_URL,
  [string]$PairingCode = $env:GAS_PAIRING_CODE,
  [string]$InstallDir = (Join-Path $env:ProgramData "gas-agent"),
  [string]$ServiceName = "gas-agent",
  [int]$PollInterval = 5,
  [switch]$BreakGlassEnabled,
  [switch]$NoService,
  [string]$AgentName = $env:AGENT_NAME,
  [string]$Labels = $env:LABELS,
  [string]$TenantId = $env:GAS_TENANT_ID,
  [string]$WorkspaceId = $env:GAS_WORKSPACE_ID,
  [string]$NssmPath = $env:NSSM_PATH
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-IsAdmin {
  try {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $p = New-Object Security.Principal.WindowsPrincipal($id)
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
  } catch {
    return $false
  }
}

function Normalize-Url([string]$Url) {
  if ($null -eq $Url) { $Url = "" }
  $u = ([string]$Url).Trim()
  while ($u.EndsWith("/")) { $u = $u.Substring(0, $u.Length - 1) }
  return $u
}

function Parse-Labels([string]$Raw) {
  $out = @{}
  if (-not $Raw) { return $out }
  $s = $Raw.Trim()
  if (-not $s) { return $out }
  if ($s.StartsWith("{")) {
    try {
      $obj = $s | ConvertFrom-Json
      if ($null -ne $obj) {
        $obj.PSObject.Properties | ForEach-Object { $out[$_.Name] = [string]$_.Value }
        return $out
      }
    } catch {
      return $out
    }
  }
  $pairs = $s.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ }
  foreach ($p in $pairs) {
    if ($p -notmatch "=") { continue }
    $kv = $p.Split("=", 2)
    $k = ""
    if ($kv.Count -ge 1 -and $null -ne $kv[0]) { $k = ([string]$kv[0]).Trim() }
    $v = ""
    if ($kv.Count -ge 2 -and $null -ne $kv[1]) { $v = ([string]$kv[1]).Trim() }
    if ($k) { $out[$k] = $v }
  }
  return $out
}

function Resolve-Python {
  $py = Get-Command "python" -ErrorAction SilentlyContinue
  if ($py) { return @($py.Source) }
  $launcher = Get-Command "py" -ErrorAction SilentlyContinue
  if ($launcher) { return @($launcher.Source, "-3") }
  return $null
}

function Install-GasAgent {
  param(
    [string]$ControlPlaneUrl,
    [string]$PairingCode,
    [string]$InstallDir,
    [string]$ServiceName,
    [int]$PollInterval,
    [bool]$BreakGlassEnabled,
    [bool]$NoService,
    [string]$AgentName,
    [string]$Labels,
    [string]$TenantId,
    [string]$WorkspaceId,
    [string]$NssmPath
  )

  $ControlPlaneUrl = Normalize-Url $ControlPlaneUrl
  if (-not $ControlPlaneUrl) { throw "CONTROL_PLANE_URL is required." }

  $stateDir = Join-Path $InstallDir "state"
  $configPath = Join-Path $InstallDir "agent_config.json"
  $venvDir = Join-Path $InstallDir ".venv"

  New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
  New-Item -ItemType Directory -Force -Path $stateDir | Out-Null

  Write-Host "GAS control plane: $ControlPlaneUrl"
  Write-Host "Install dir:      $InstallDir"
  Write-Host "State dir:        $stateDir"

  $tmp = Join-Path $env:TEMP ("gas-agent-" + [Guid]::NewGuid().ToString("n"))
  New-Item -ItemType Directory -Force -Path $tmp | Out-Null

  try {
    $zipUrl = "$ControlPlaneUrl/install/agent.zip"
    $zipPath = Join-Path $tmp "agent.zip"
    Write-Host "Downloading agent: $zipUrl"
    if ($PSVersionTable.PSVersion.Major -lt 6) {
      Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
    } else {
      Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath
    }

    $agentDir = Join-Path $InstallDir "agent"
    if (Test-Path $agentDir) {
      Remove-Item -Recurse -Force $agentDir
    }
    Expand-Archive -Path $zipPath -DestinationPath $InstallDir -Force

    $labelsObj = Parse-Labels $Labels
    $resolvedAgentName = $AgentName
    if (-not $resolvedAgentName) { $resolvedAgentName = $env:COMPUTERNAME }
    $cfg = @{
      control_plane_url = $ControlPlaneUrl
      agent_name = $resolvedAgentName
      tenant_id = $TenantId
      workspace_id = $WorkspaceId
      labels = $labelsObj
      poll_interval = $PollInterval
      break_glass_enabled = [bool]$BreakGlassEnabled
    }
    $cfg | ConvertTo-Json -Depth 6 | Out-File -FilePath $configPath -Encoding utf8

    $py = Resolve-Python
    if (-not $py) { throw "Python not found (expected 'python' or 'py'). Install Python 3.11+ first." }

    if (-not (Test-Path $venvDir)) {
      Write-Host "Creating venv: $venvDir"
      & $py -m venv $venvDir
    }

    $pythonExe = Join-Path $venvDir "Scripts\\python.exe"
    if (-not (Test-Path $pythonExe)) { throw "Venv python not found at $pythonExe" }

    Write-Host "Pairing/registering agent (token is stored locally; never printed)..."
    $env:GAS_HOME = $stateDir
    $env:CONTROL_PLANE_URL = $ControlPlaneUrl
    $env:PYTHONPATH = $InstallDir
    if ($PairingCode) { $env:GAS_PAIRING_CODE = $PairingCode }

    & $pythonExe -m agent --config $configPath --register-only

    if ($NoService) {
      Write-Host "Skipping service install (NoService=true)."
      return
    }

    $isAdmin = Test-IsAdmin
    if (-not $isAdmin) {
      Write-Warning "Not running as Administrator; skipping service install. Re-run PowerShell as Admin to install the service."
      return
    }

    $nssm = $null
    if ($NssmPath -and (Test-Path $NssmPath)) {
      $nssm = $NssmPath
    } else {
      $cmd = Get-Command "nssm" -ErrorAction SilentlyContinue
      if ($cmd) { $nssm = $cmd.Source }
    }

    if ($nssm) {
      Write-Host "Installing Windows service via NSSM: $ServiceName"
      & $nssm install $ServiceName $pythonExe "-m agent --config `"$configPath`""
      & $nssm set $ServiceName AppDirectory $InstallDir
      & $nssm set $ServiceName Start SERVICE_AUTO_START
      & $nssm set $ServiceName AppExit Default Restart
      & $nssm set $ServiceName AppRestartDelay 5000

      $stdoutPath = Join-Path $stateDir "nssm.stdout.log"
      $stderrPath = Join-Path $stateDir "nssm.stderr.log"
      & $nssm set $ServiceName AppStdout $stdoutPath
      & $nssm set $ServiceName AppStderr $stderrPath
      & $nssm set $ServiceName AppRotateFiles 1
      & $nssm set $ServiceName AppRotateBytes 10485760

      $envLines = @(
        "GAS_HOME=$stateDir",
        "CONTROL_PLANE_URL=$ControlPlaneUrl",
        "PYTHONPATH=$InstallDir",
        "GAS_LOG_MAX_BYTES=5000000",
        "GAS_LOG_BACKUP_COUNT=5"
      ) -join "`r`n"
      & $nssm set $ServiceName AppEnvironmentExtra $envLines

      & $nssm start $ServiceName
      Write-Host "Service started: $ServiceName"
      return
    }

    Write-Warning "NSSM not found; falling back to built-in Windows Service (sc.exe)."
    Write-Host "Setting machine env: GAS_HOME=$stateDir"
    [Environment]::SetEnvironmentVariable("GAS_HOME", $stateDir, "Machine") | Out-Null
    [Environment]::SetEnvironmentVariable("CONTROL_PLANE_URL", $ControlPlaneUrl, "Machine") | Out-Null
    $existingPythonPath = [Environment]::GetEnvironmentVariable("PYTHONPATH", "Machine")
    if (-not $existingPythonPath) {
      [Environment]::SetEnvironmentVariable("PYTHONPATH", $InstallDir, "Machine") | Out-Null
    } elseif ($existingPythonPath -notlike "*$InstallDir*") {
      [Environment]::SetEnvironmentVariable("PYTHONPATH", ($InstallDir + ";" + $existingPythonPath), "Machine") | Out-Null
    }
    [Environment]::SetEnvironmentVariable("GAS_LOG_MAX_BYTES", "5000000", "Machine") | Out-Null
    [Environment]::SetEnvironmentVariable("GAS_LOG_BACKUP_COUNT", "5", "Machine") | Out-Null

    $binPath = "`"$pythonExe`" -m agent --config `"$configPath`""
    & sc.exe create $ServiceName binPath= $binPath start= auto | Out-Null
    & sc.exe description $ServiceName "Graph Admin Studio execution agent" | Out-Null
    & sc.exe start $ServiceName | Out-Null
    Write-Host "Service started: $ServiceName"
  } finally {
    try { Remove-Item -Recurse -Force $tmp } catch { }
  }
}

function Uninstall-GasAgent {
  param(
    [string]$ServiceName = "gas-agent",
    [string]$InstallDir = (Join-Path $env:ProgramData "gas-agent")
  )

  $isAdmin = Test-IsAdmin
  if (-not $isAdmin) { throw "Administrator privileges required to remove a service." }

  $nssmCmd = Get-Command "nssm" -ErrorAction SilentlyContinue
  if ($nssmCmd) {
    try { & $nssmCmd.Source stop $ServiceName | Out-Null } catch { }
    try { & $nssmCmd.Source remove $ServiceName confirm | Out-Null } catch { }
  } else {
    try { & sc.exe stop $ServiceName | Out-Null } catch { }
    try { & sc.exe delete $ServiceName | Out-Null } catch { }
  }

  if (Test-Path $InstallDir) {
    Remove-Item -Recurse -Force $InstallDir
  }
  Write-Host "Removed service and install dir."
}

Install-GasAgent `
  -ControlPlaneUrl $ControlPlaneUrl `
  -PairingCode $PairingCode `
  -InstallDir $InstallDir `
  -ServiceName $ServiceName `
  -PollInterval $PollInterval `
  -BreakGlassEnabled ([bool]$BreakGlassEnabled) `
  -NoService ([bool]$NoService) `
  -AgentName $AgentName `
  -Labels $Labels `
  -TenantId $TenantId `
  -WorkspaceId $WorkspaceId `
  -NssmPath $NssmPath
