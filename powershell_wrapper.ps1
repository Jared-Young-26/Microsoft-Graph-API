param(
  [Parameter(Mandatory = $true)]
  [string]$Command,
  [string[]]$Modules = @(),
  [int]$TimeoutSeconds = 0,
  [string]$WorkingDirectory = ""
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$Error.Clear()

function Get-ErrorInfo {
  param($err)
  if (-not $err) { return $null }
  [PSCustomObject]@{
    message = $err.Exception.Message
    type = $err.Exception.GetType().FullName
    category = $err.CategoryInfo.Reason
    fully_qualified_error_id = $err.FullyQualifiedErrorId
    script_stack_trace = $err.ScriptStackTrace
    details = ($err | Out-String).Trim()
  }
}

function Get-NonTerminatingErrors {
  $Error | ForEach-Object {
    [PSCustomObject]@{
      message = $_.Exception.Message
      type = $_.Exception.GetType().FullName
      category = $_.CategoryInfo.Reason
      fully_qualified_error_id = $_.FullyQualifiedErrorId
    }
  }
}

function Import-ModulesWithDiagnostics {
  param([string[]]$ModuleNames)
  $results = @()
  foreach ($m in $ModuleNames) {
    if (-not $m) { continue }
    try {
      Import-Module $m -ErrorAction Stop | Out-Null
      $version = $null
      try {
        $version = (Get-Module $m | Select-Object -First 1 -ExpandProperty Version)
      } catch {}
      $results += [PSCustomObject]@{
        name = $m
        ok = $true
        version = if ($version) { "$version" } else { $null }
      }
    } catch {
      $results += [PSCustomObject]@{
        name = $m
        ok = $false
        error = $_.Exception.Message
      }
    }
  }
  return $results
}

function Invoke-CommandEnvelope {
  param(
    [string]$Cmd,
    [string[]]$ModuleNames,
    [string]$WorkDir
  )

  $execError = $null
  $data = $null
  $moduleResults = Import-ModulesWithDiagnostics -ModuleNames $ModuleNames
  $start = Get-Date

  try {
    if ($WorkDir) {
      Push-Location $WorkDir
    }
    $data = & ([scriptblock]::Create($Cmd))
  } catch {
    $execError = $_
  } finally {
    if ($WorkDir) {
      Pop-Location
    }
  }

  $end = Get-Date
  [PSCustomObject]@{
    ok = ($execError -eq $null)
    data = $data
    error = Get-ErrorInfo -err $execError
    meta = [PSCustomObject]@{
      started_at = $start.ToString("o")
      ended_at = $end.ToString("o")
      duration_ms = [math]::Round(($end - $start).TotalMilliseconds, 2)
      error_count = $Error.Count
      non_terminating_errors = Get-NonTerminatingErrors
      module_imports = $moduleResults
      working_directory = $WorkDir
    }
  }
}

$envelope = $null

if ($TimeoutSeconds -gt 0) {
  $job = Start-Job -ScriptBlock ${function:Invoke-CommandEnvelope} -ArgumentList $Command, $Modules, $WorkingDirectory
  $completed = Wait-Job -Job $job -Timeout $TimeoutSeconds
  if (-not $completed) {
    Stop-Job $job -Force | Out-Null
    Remove-Job $job | Out-Null
    $envelope = [PSCustomObject]@{
      ok = $false
      data = $null
      error = [PSCustomObject]@{
        message = "Timeout after ${TimeoutSeconds}s"
        type = "Timeout"
        category = "Timeout"
        fully_qualified_error_id = "Timeout"
        script_stack_trace = $null
        details = $null
      }
      meta = [PSCustomObject]@{
        started_at = (Get-Date).ToString("o")
        ended_at = (Get-Date).ToString("o")
        duration_ms = 0
        error_count = 0
        non_terminating_errors = @()
        module_imports = Import-ModulesWithDiagnostics -ModuleNames $Modules
        working_directory = $WorkingDirectory
        timeout_seconds = $TimeoutSeconds
      }
    }
  } else {
    $envelope = Receive-Job $job
    Remove-Job $job | Out-Null
  }
} else {
  $envelope = Invoke-CommandEnvelope -Cmd $Command -ModuleNames $Modules -WorkDir $WorkingDirectory
}

$envelope | ConvertTo-Json -Depth 8 -Compress
