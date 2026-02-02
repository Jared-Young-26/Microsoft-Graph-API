from __future__ import annotations

from datetime import datetime, timezone
from ipaddress import ip_address, ip_network
from typing import Any, Dict, Optional

from microsoft import is_powershell_envelope, unwrap_powershell_data


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _wrap_envelope(result, payload_builder):
    if is_powershell_envelope(result):
        if not result.get("ok", True):
            return result
        data = unwrap_powershell_data(result)
        payload = payload_builder(data)
        return {**result, "data": payload}
    return payload_builder(result)


def _read_inputs(options: Dict[str, Any]) -> Dict[str, Any]:
    inputs = options.get("inputs") if isinstance(options, dict) else None
    return dict(inputs or {})


def _ps_run(context: Dict[str, Any], script: str, parameters: Optional[Dict[str, Any]] = None, depth: int = 8):
    session = context.get("powershell")
    if not session:
        return {"ok": False, "data": None, "error": {"message": "PowerShell session missing."}, "meta": {}}
    return session.run_json(script, parameters=parameters, depth=depth)


def _apply_time_warnings(payload: Dict[str, Any], thresholds: Dict[str, Any]) -> Dict[str, Any]:
    warn_ms = thresholds.get("warn_ms", 300)
    high_ms = thresholds.get("high_ms", 5000)
    warnings = payload.get("warnings") or []
    for key in ("offset_ms", "dc_offset_ms", "ntp_offset_ms"):
        value = payload.get(key)
        if value is None:
            continue
        try:
            magnitude = abs(float(value))
        except Exception:
            continue
        if magnitude >= high_ms:
            warnings.append(f"time.skew_detected: {key}={value}ms")
        elif magnitude >= warn_ms:
            warnings.append(f"time.skew_warning: {key}={value}ms")
    payload["warnings"] = warnings
    return payload


def local_system_info_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    script = r"""
$cs = Get-CimInstance Win32_ComputerSystem | Select-Object Name,Domain,Manufacturer,Model,TotalPhysicalMemory
$os = Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,LastBootUpTime,OSArchitecture
$uptimeSeconds = $null
if ($os.LastBootUpTime) {
  try { $uptimeSeconds = [math]::Round(((Get-Date) - $os.LastBootUpTime).TotalSeconds, 0) } catch { $uptimeSeconds = $null }
}
[PSCustomObject]@{
  hostname = $cs.Name
  domain = $cs.Domain
  manufacturer = $cs.Manufacturer
  model = $cs.Model
  os_name = $os.Caption
  os_version = $os.Version
  os_build = $os.BuildNumber
  os_architecture = $os.OSArchitecture
  last_boot = $os.LastBootUpTime
  uptime_seconds = $uptimeSeconds
}
"""
    return _ps_run(context, script)


def local_interfaces_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    script = r"""
$rows = Get-NetIPConfiguration | ForEach-Object {
  [PSCustomObject]@{
    name = $_.InterfaceAlias
    interface_index = $_.InterfaceIndex
    ipv4 = ($_.IPv4Address | ForEach-Object { $_.IPAddress })
    ipv6 = ($_.IPv6Address | ForEach-Object { $_.IPAddress })
    dns_servers = $_.DnsServer.ServerAddresses
    gateway = if ($_.IPv4DefaultGateway) { $_.IPv4DefaultGateway.NextHop } else { $null }
  }
}
$rows
"""
    return _ps_run(context, script)


def local_routes_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    script = r"""
$routes = Get-NetRoute -AddressFamily IPv4 | Select-Object DestinationPrefix,NextHop,InterfaceAlias,RouteMetric
$default = $routes | Where-Object { $_.DestinationPrefix -eq '0.0.0.0/0' } | Select-Object -First 1
[PSCustomObject]@{
  default_gw = if ($default) { $default.NextHop } else { $null }
  routes = $routes
}
"""
    return _ps_run(context, script, depth=6)


def dns_resolve_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    inputs = _read_inputs(options)
    targets = inputs.get("targets") or []
    script = r"""
param($targets)
$results = @()
foreach ($target in $targets) {
  if (-not $target) { continue }
  try {
    $res = Resolve-DnsName -Name $target -ErrorAction Stop
    $addresses = $res | Where-Object { $_.IPAddress } | Select-Object -ExpandProperty IPAddress
    $server = ($res | Select-Object -First 1).Server
    $results += [PSCustomObject]@{
      name = 'dns_resolve'
      target = $target
      ok = $true
      addresses = $addresses
      server = $server
    }
  } catch {
    $results += [PSCustomObject]@{
      name = 'dns_resolve'
      target = $target
      ok = $false
      error = $_.Exception.Message
    }
  }
}
$results
"""
    return _ps_run(context, script, parameters={"targets": targets}, depth=6)


def port_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    inputs = _read_inputs(options)
    targets = inputs.get("targets") or []
    ports = inputs.get("ports") or []
    script = r"""
param($targets, $ports)
$results = @()
foreach ($target in $targets) {
  foreach ($port in $ports) {
    if (-not $target -or -not $port) { continue }
    try {
      $res = Test-NetConnection -ComputerName $target -Port $port -InformationLevel Detailed
      $results += [PSCustomObject]@{
        name = 'port_probe'
        target = $target
        port = $port
        reachable = $res.TcpTestSucceeded
        remote_address = $res.RemoteAddress
        interface = $res.InterfaceAlias
        latency_ms = if ($res.PingSucceeded) { $res.PingReplyDetails.RoundtripTime } else { $null }
      }
    } catch {
      $results += [PSCustomObject]@{
        name = 'port_probe'
        target = $target
        port = $port
        reachable = $false
        error = $_.Exception.Message
      }
    }
  }
}
$results
"""
    return _ps_run(context, script, parameters={"targets": targets, "ports": ports}, depth=6)


def firewall_profiles_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    script = r"""
Get-NetFirewallProfile | Select-Object Name,Enabled,DefaultInboundAction,DefaultOutboundAction
"""
    return _ps_run(context, script, depth=4)


def eventlog_summary_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    inputs = _read_inputs(options)
    log_names = inputs.get("log_names") or ["System", "Application"]
    levels = inputs.get("levels") or ["Error", "Warning"]
    hours = inputs.get("time_window_hours") or 24
    event_ids = inputs.get("event_ids")
    providers = inputs.get("providers")
    max_events = inputs.get("max_events") or 500
    sample_size = inputs.get("sample_size") or 10
    script = r"""
param($logNames, $levels, $hours, $eventIds, $providers, $maxEvents, $sampleSize)
$levelMap = @{
  "critical" = 1
  "error" = 2
  "warning" = 3
  "information" = 4
  "verbose" = 5
}
$levelNums = @()
foreach ($lvl in ($levels | Where-Object { $_ -ne $null -and $_ -ne "" })) {
  if ($lvl -is [int]) {
    $levelNums += [int]$lvl
  } else {
    $key = "$lvl".ToLower()
    if ($levelMap.ContainsKey($key)) { $levelNums += $levelMap[$key] }
  }
}
$startTime = $null
if ($hours) { $startTime = (Get-Date).AddHours(-1 * [double]$hours) }
$events = @()
foreach ($logName in ($logNames | Where-Object { $_ -ne $null -and $_ -ne "" })) {
  $filter = @{ LogName = $logName }
  if ($startTime) { $filter.StartTime = $startTime }
  if ($levelNums.Count -gt 0) { $filter.Level = $levelNums }
  if ($eventIds) { $filter.Id = $eventIds }
  if ($providers) { $filter.ProviderName = $providers }
  try {
    $events += Get-WinEvent -FilterHashtable $filter -MaxEvents $maxEvents -ErrorAction Stop
  } catch {
    # ignore per-log failures
  }
}
$levelCounts = @{}
$providerCounts = @{}
$idCounts = @{}
$lastError = $null
foreach ($evt in $events) {
  $lvl = $evt.LevelDisplayName
  if (-not $lvl) { $lvl = "Unknown" }
  if (-not $levelCounts.ContainsKey($lvl)) { $levelCounts[$lvl] = 0 }
  $levelCounts[$lvl] += 1
  $prov = $evt.ProviderName
  if ($prov) {
    if (-not $providerCounts.ContainsKey($prov)) { $providerCounts[$prov] = 0 }
    $providerCounts[$prov] += 1
  }
  $id = $evt.Id
  if ($id) {
    if (-not $idCounts.ContainsKey($id)) { $idCounts[$id] = 0 }
    $idCounts[$id] += 1
  }
  if ($evt.LevelDisplayName -in @("Error", "Critical")) {
    if (-not $lastError -or $evt.TimeCreated -gt $lastError) { $lastError = $evt.TimeCreated }
  }
}
$topIds = $idCounts.GetEnumerator() | Sort-Object -Property Value -Descending | Select-Object -First 10 |
  ForEach-Object { [PSCustomObject]@{ event_id = $_.Key; count = $_.Value } }
$topProviders = $providerCounts.GetEnumerator() | Sort-Object -Property Value -Descending | Select-Object -First 10 |
  ForEach-Object { [PSCustomObject]@{ provider = $_.Key; count = $_.Value } }
$sample = $events | Sort-Object TimeCreated -Descending | Select-Object -First $sampleSize |
  ForEach-Object {
    $msg = $_.Message
    if ($msg -and $msg.Length -gt 300) { $msg = $msg.Substring(0,300) + "..." }
    [PSCustomObject]@{
      time_created = $_.TimeCreated
      event_id = $_.Id
      level = $_.LevelDisplayName
      provider = $_.ProviderName
      machine = $_.MachineName
      message = $msg
    }
  }
[PSCustomObject]@{
  total_events = $events.Count
  levels = $levelCounts
  top_event_ids = $topIds
  top_providers = $topProviders
  last_error_time = $lastError
  sample_events = $sample
}
"""
    return _ps_run(
        context,
        script,
        parameters={
            "logNames": log_names,
            "levels": levels,
            "hours": hours,
            "eventIds": event_ids,
            "providers": providers,
            "maxEvents": max_events,
            "sampleSize": sample_size,
        },
        depth=6,
    )


def registry_watchlist_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    inputs = _read_inputs(options)
    watchlist_id = inputs.get("watchlist_id")
    watchlists = context.get("registry_watchlists") or {}
    if not watchlists:
        return {"ok": False, "error": {"message": "Registry watchlists missing."}, "data": {"missing": "watchlists"}}
    if not watchlist_id:
        watchlist_id = next(iter(watchlists.keys()))
    watchlist = watchlists.get(watchlist_id)
    if not watchlist:
        return {"ok": False, "error": {"message": "Watchlist not found."}, "data": {"missing": watchlist_id}}
    paths = watchlist.get("paths") or []
    recurse_depth = int(inputs.get("recurse_depth") or 0)
    max_items = int(inputs.get("max_items") or 200)
    script = r"""
param($paths, $depth, $maxItems)
$results = New-Object System.Collections.ArrayList
function Get-ValueHash($value) {
  try {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes([string]$value)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $hash = $sha.ComputeHash($bytes)
    return ([System.BitConverter]::ToString($hash)).Replace('-', '').ToLower()
  } catch { return $null }
}
function Normalize-Value($name, $value) {
  if ($null -eq $value) { return $null }
  if ($value -is [byte[]]) { return "sha256:" + (Get-ValueHash ([System.Convert]::ToBase64String($value))) }
  if ($value -is [string]) {
    $lower = $name.ToLower()
    if ($lower -match "password|secret|token|key|credential") { return "[redacted]" }
    if ($value.Length -gt 120) { return "sha256:" + (Get-ValueHash $value) }
    return $value
  }
  if ($value -is [int] -or $value -is [long] -or $value -is [double]) { return $value }
  return "sha256:" + (Get-ValueHash ($value | Out-String))
}
function Add-Entry($path) {
  if ($results.Count -ge $maxItems) { return }
  if (-not (Test-Path $path)) { return }
  try {
    $item = Get-Item -Path $path -ErrorAction Stop
    $props = Get-ItemProperty -Path $path -ErrorAction Stop
    $values = @{}
    $types = @{}
    foreach ($prop in $props.PSObject.Properties) {
      if ($prop.Name -in "PSPath","PSParentPath","PSChildName","PSDrive","PSProvider") { continue }
      $values[$prop.Name] = (Normalize-Value $prop.Name $prop.Value)
      $types[$prop.Name] = $prop.TypeNameOfValue
    }
    $entry = [PSCustomObject]@{
      path = $path
      values = $values
      value_types = $types
      last_write_time = $item.LastWriteTime
    }
    [void]$results.Add($entry)
  } catch {
    $entry = [PSCustomObject]@{ path = $path; error = $_.Exception.Message }
    [void]$results.Add($entry)
  }
}
function Walk-Registry($path, $depth) {
  Add-Entry $path
  if ($depth -le 0 -or $results.Count -ge $maxItems) { return }
  try {
    $children = Get-ChildItem -Path $path -ErrorAction SilentlyContinue
    foreach ($child in $children) {
      if ($results.Count -ge $maxItems) { return }
      Walk-Registry $child.PSPath ($depth - 1)
    }
  } catch { return }
}
foreach ($path in ($paths | Where-Object { $_ -ne $null -and $_ -ne "" })) {
  Walk-Registry $path $depth
}
[PSCustomObject]@{ count = $results.Count; items = $results }
"""
    result = _ps_run(context, script, parameters={"paths": paths, "depth": recurse_depth, "maxItems": max_items}, depth=6)

    def _build(data):
        payload = data if isinstance(data, dict) else {}
        return {"watchlist_id": watchlist_id, "items": payload.get("items") or []}

    return _wrap_envelope(result, _build)


def time_local_status_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    script = r"""
$raw = w32tm /query /status 2>&1
$map = @{}
foreach ($line in ($raw -split "`r?`n")) {
  if ($line -match '^\s*([^:]+):\s*(.*)$') {
    $map[$matches[1].Trim()] = $matches[2].Trim()
  }
}
$offsetSeconds = $null
if ($map.ContainsKey('Phase Offset') -and ($map['Phase Offset'] -match '([+-]?\d+(\.\d+)?)s')) {
  $offsetSeconds = [double]$matches[1]
} elseif ($map.ContainsKey('Offset') -and ($map['Offset'] -match '([+-]?\d+(\.\d+)?)s')) {
  $offsetSeconds = [double]$matches[1]
}
[PSCustomObject]@{
  local_time = (Get-Date).ToString('o')
  source = $map['Source']
  stratum = $map['Stratum']
  last_sync = $map['Last Successful Sync Time']
  offset_ms = if ($offsetSeconds -ne $null) { [math]::Round($offsetSeconds * 1000, 2) } else { $null }
  status = $map
}
"""
    result = _ps_run(context, script)

    def _build(data):
        payload = data if isinstance(data, dict) else {}
        thresholds = context.get("time_thresholds") or {}
        return _apply_time_warnings(payload, thresholds)

    return _wrap_envelope(result, _build)


def time_dc_offset_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    script = r"""
$raw = w32tm /monitor 2>&1
$entries = @()
foreach ($line in ($raw -split "`r?`n")) {
  if ($line -match '^\s*([^\s]+).*?offset:\s*([+-]?\d+(\.\d+)?)s') {
    $entries += [PSCustomObject]@{
      target = $matches[1]
      offset_ms = [math]::Round(([double]$matches[2]) * 1000, 2)
    }
  }
}
[PSCustomObject]@{
  dc_offsets = $entries
  dc_offset_ms = if ($entries.Count -gt 0) { $entries[0].offset_ms } else { $null }
  raw_text = $raw
}
"""
    result = _ps_run(context, script)

    def _build(data):
        payload = data if isinstance(data, dict) else {}
        thresholds = context.get("time_thresholds") or {}
        return _apply_time_warnings(payload, thresholds)

    return _wrap_envelope(result, _build)


def time_ntp_offset_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    inputs = _read_inputs(options)
    servers = inputs.get("servers") or ["pool.ntp.org"]
    samples = int(inputs.get("samples") or 3)
    script = r"""
param($servers, $samples)
$results = @()
foreach ($server in $servers) {
  if (-not $server) { continue }
  $raw = w32tm /stripchart /computer:$server /dataonly /samples:$samples 2>&1
  $offsets = @()
  foreach ($line in ($raw -split "`r?`n")) {
    if ($line -match '([+-]?\d+(\.\d+)?)s') {
      $offsets += [double]$matches[1]
    }
  }
  $avg = $null
  if ($offsets.Count -gt 0) {
    $avg = [math]::Round((($offsets | Measure-Object -Average).Average) * 1000, 2)
  }
  $results += [PSCustomObject]@{
    server = $server
    ntp_offset_ms = $avg
    samples = $offsets.Count
    raw_text = $raw
  }
}
[PSCustomObject]@{
  ntp_offsets = $results
  ntp_offset_ms = if ($results.Count -gt 0) { $results[0].ntp_offset_ms } else { $null }
}
"""
    result = _ps_run(context, script, parameters={"servers": servers, "samples": samples})

    def _build(data):
        payload = data if isinstance(data, dict) else {}
        thresholds = context.get("time_thresholds") or {}
        return _apply_time_warnings(payload, thresholds)

    return _wrap_envelope(result, _build)


def cert_inventory_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    inputs = _read_inputs(options)
    stores = inputs.get("stores") or ["My", "Root", "CA"]
    expiring_days = int(inputs.get("expiring_days") or 30)
    script = r"""
param($stores, $expiring_days)
$deadline = (Get-Date).AddDays($expiring_days)
$results = @()
foreach ($store in $stores) {
  if (-not $store) { continue }
  $path = "Cert:\\LocalMachine\\$store"
  if (-not (Test-Path $path)) { continue }
  Get-ChildItem -Path $path | ForEach-Object {
    $eku = @()
    if ($_.EnhancedKeyUsageList) {
      $eku = $_.EnhancedKeyUsageList | ForEach-Object { $_.FriendlyName }
    }
    $isExpiring = $false
    if ($_.NotAfter -and $_.NotAfter -le $deadline) {
      $isExpiring = $true
    }
    $results += [PSCustomObject]@{
      store = $store
      subject = $_.Subject
      issuer = $_.Issuer
      not_before = $_.NotBefore.ToString('o')
      not_after = $_.NotAfter.ToString('o')
      has_private_key = $_.HasPrivateKey
      thumbprint = $_.Thumbprint
      serial_number = $_.SerialNumber
      eku = $eku
      is_expiring_soon = $isExpiring
    }
  }
}
$results
"""
    return _ps_run(context, script, parameters={"stores": stores, "expiring_days": expiring_days}, depth=6)


def tls_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    inputs = _read_inputs(options)
    targets = inputs.get("targets") or []
    port = int(inputs.get("port") or 443)
    script = r"""
param($targets, $port)
$results = @()
foreach ($target in $targets) {
  if (-not $target) { continue }
  $host = $target
  $targetPort = $port
  if ($target -match '^(?<h>[^:]+):(?<p>\d+)$') {
    $host = $matches['h']
    $targetPort = [int]$matches['p']
  }
  $client = $null
  $ssl = $null
  try {
    $client = New-Object System.Net.Sockets.TcpClient($host, $targetPort)
    $ssl = New-Object System.Net.Security.SslStream($client.GetStream(), $false, ({$true}))
    $ssl.AuthenticateAsClient($host)
    $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($ssl.RemoteCertificate)
    $chain = New-Object System.Security.Cryptography.X509Certificates.X509Chain
    $null = $chain.Build($cert)
    $status = $chain.ChainStatus | ForEach-Object { $_.Status.ToString() }
    $results += [PSCustomObject]@{
      target = $host
      port = $targetPort
      ok = $true
      subject = $cert.Subject
      issuer = $cert.Issuer
      not_before = $cert.NotBefore.ToString('o')
      not_after = $cert.NotAfter.ToString('o')
      thumbprint = $cert.Thumbprint
      chain_ok = ($chain.ChainStatus.Count -eq 0)
      chain_status = $status
      protocol = $ssl.SslProtocol.ToString()
      cipher = $ssl.CipherAlgorithm.ToString()
      cipher_strength = $ssl.CipherStrength
    }
  } catch {
    $results += [PSCustomObject]@{
      target = $host
      port = $targetPort
      ok = $false
      error = $_.Exception.Message
    }
  } finally {
    if ($ssl) { $ssl.Dispose() }
    if ($client) { $client.Close() }
  }
}
$results
"""
    return _ps_run(context, script, parameters={"targets": targets, "port": port}, depth=6)


def process_inventory_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    inputs = _read_inputs(options)
    include_command_line = bool(inputs.get("include_command_line", False))
    max_items = int(inputs.get("max_items") or 200)
    script = r"""
param($include_command_line, $max_items)
$cmdLines = @{}
if ($include_command_line) {
  try {
    Get-CimInstance Win32_Process | ForEach-Object { $cmdLines[$_.ProcessId] = $_.CommandLine }
  } catch {}
}
$rows = Get-Process | Sort-Object CPU -Descending | Select-Object -First $max_items Name,Id,CPU,WS,StartTime,Path
$results = @()
foreach ($p in $rows) {
  $sig = $null
  if ($p.Path) {
    try { $sig = Get-AuthenticodeSignature -FilePath $p.Path } catch {}
  }
  $results += [PSCustomObject]@{
    name = $p.Name
    pid = $p.Id
    cpu = $p.CPU
    memory_bytes = $p.WS
    start_time = if ($p.StartTime) { $p.StartTime.ToString('o') } else { $null }
    path = $p.Path
    command_line = if ($include_command_line) { $cmdLines[$p.Id] } else { $null }
    signed = if ($sig) { ($sig.Status -eq 'Valid') } else { $null }
    signer = if ($sig -and $sig.SignerCertificate) { $sig.SignerCertificate.Subject } else { $null }
    signature_status = if ($sig) { $sig.Status.ToString() } else { $null }
  }
}
$results
"""
    result = _ps_run(
        context,
        script,
        parameters={"include_command_line": include_command_line, "max_items": max_items},
        depth=6,
    )

    def _build(data):
        rows = data if isinstance(data, list) else []
        summary = {
            "count": len(rows),
            "top_cpu": rows[:5],
            "top_mem": sorted(rows, key=lambda r: r.get("memory_bytes") or 0, reverse=True)[:5],
        }
        suspicious = []
        for row in rows:
            path = (row.get("path") or "").lower()
            signed = row.get("signed")
            if path and ("\\windows\\system32" in path or "\\windows\\" in path):
                if signed is False:
                    suspicious.append({**row, "reason": "unsigned_system_path"})
            if path and ("\\temp\\" in path or "\\appdata\\local\\temp" in path):
                suspicious.append({**row, "reason": "temp_path_execution"})
        return {
            "summary": summary,
            "suspicious": suspicious,
            "processes": rows,
        }

    return _wrap_envelope(result, _build)


def service_process_map_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    inputs = _read_inputs(options)
    max_items = int(inputs.get("max_items") or 200)
    script = r"""
param($max_items)
$services = Get-CimInstance Win32_Service | Select-Object Name,DisplayName,State,Status,StartMode,ProcessId
$processes = Get-Process | Select-Object Id,Name,Path
$map = @{}
foreach ($p in $processes) { $map[$p.Id] = $p }
$rows = @()
foreach ($svc in $services) {
  $proc = $null
  if ($svc.ProcessId -and $map.ContainsKey($svc.ProcessId)) { $proc = $map[$svc.ProcessId] }
  $rows += [PSCustomObject]@{
    name = $svc.Name
    display_name = $svc.DisplayName
    state = $svc.State
    status = $svc.Status
    start_mode = $svc.StartMode
    process_id = $svc.ProcessId
    process_name = if ($proc) { $proc.Name } else { $null }
    process_path = if ($proc) { $proc.Path } else { $null }
  }
}
$rows | Select-Object -First $max_items
"""
    return _ps_run(context, script, parameters={"max_items": max_items}, depth=6)


def resource_pressure_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    script = r"""
$cpu = $null
try {
  $cpu = (Get-Counter '\\Processor(_Total)\\% Processor Time').CounterSamples[0].CookedValue
} catch {}
$os = Get-CimInstance Win32_OperatingSystem
$totalMem = if ($os.TotalVisibleMemorySize) { $os.TotalVisibleMemorySize * 1KB } else { $null }
$freeMem = if ($os.FreePhysicalMemory) { $os.FreePhysicalMemory * 1KB } else { $null }
$memUsedPct = $null
if ($totalMem -and $freeMem -ne $null) {
  $memUsedPct = [math]::Round((($totalMem - $freeMem) / $totalMem) * 100, 2)
}
$disks = @()
Get-PSDrive -PSProvider FileSystem | ForEach-Object {
  $freePct = $null
  if ($_.Used -ne $null -and $_.Free -ne $null) {
    $total = $_.Used + $_.Free
    if ($total -gt 0) { $freePct = [math]::Round(($_.Free / $total) * 100, 2) }
  }
  $disks += [PSCustomObject]@{
    name = $_.Name
    root = $_.Root
    free_bytes = $_.Free
    used_bytes = $_.Used
    free_percent = $freePct
  }
}
[PSCustomObject]@{
  cpu_percent = if ($cpu -ne $null) { [math]::Round($cpu, 2) } else { $null }
  memory_used_percent = $memUsedPct
  memory_total_bytes = $totalMem
  memory_free_bytes = $freeMem
  disks = $disks
}
"""
    return _ps_run(context, script, depth=6)


def network_context_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    script = r"""
$cfg = Get-NetIPConfiguration | Where-Object { $_.IPv4Address -and $_.IPv4DefaultGateway } | Select-Object -First 1
$adapter = $null
if ($cfg) {
  $adapter = Get-NetAdapter -InterfaceIndex $cfg.InterfaceIndex
}
$proxyRaw = (netsh winhttp show proxy) | Out-String
$proxyPresent = -not ($proxyRaw -match 'Direct access')
$vpnPresent = $false
Get-NetAdapter | ForEach-Object {
  if ($_.Name -match 'vpn' -or $_.InterfaceDescription -match 'vpn') { $vpnPresent = $true }
}
[PSCustomObject]@{
  interface = if ($adapter) { $adapter.Name } else { $null }
  description = if ($adapter) { $adapter.InterfaceDescription } else { $null }
  ip = if ($cfg) { $cfg.IPv4Address.IPAddress } else { $null }
  prefix = if ($cfg) { $cfg.IPv4Address.PrefixLength } else { $null }
  gateway = if ($cfg) { $cfg.IPv4DefaultGateway.NextHop } else { $null }
  dns_servers = if ($cfg) { $cfg.DnsServer.ServerAddresses } else { @() }
  vpn_present = $vpnPresent
  proxy_present = $proxyPresent
  proxy_raw = $proxyRaw
}
"""
    result = _ps_run(context, script, depth=6)

    def _build(data):
        payload = data if isinstance(data, dict) else {}
        ip_value = payload.get("ip")
        zone_map = context.get("zone_map") or []
        zone = None
        site = None
        subnet = None
        if ip_value:
            try:
                ip_obj = ip_address(ip_value)
                for entry in zone_map:
                    cidr = entry.get("subnet")
                    if not cidr:
                        continue
                    try:
                        if ip_obj in ip_network(cidr, strict=False):
                            zone = entry.get("zone") or entry.get("label") or entry.get("name")
                            site = entry.get("site")
                            subnet = cidr
                            break
                    except Exception:
                        continue
            except Exception:
                pass
        payload["zone"] = zone
        payload["site"] = site
        payload["subnet"] = subnet
        return payload

    return _wrap_envelope(result, _build)


def dns_multi_resolver_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    inputs = _read_inputs(options)
    targets = inputs.get("targets") or []
    resolvers = inputs.get("resolvers") or []
    script = r"""
param($targets, $resolvers)
if (-not $resolvers -or $resolvers.Count -eq 0) {
  $resolvers = (Get-DnsClientServerAddress -AddressFamily IPv4 | Select-Object -ExpandProperty ServerAddresses -ErrorAction SilentlyContinue) | Select-Object -First 2
}
$results = @()
foreach ($target in $targets) {
  foreach ($resolver in $resolvers) {
    if (-not $target -or -not $resolver) { continue }
    try {
      $answers = Resolve-DnsName -Name $target -Server $resolver -ErrorAction Stop
      foreach ($ans in $answers) {
        $results += [PSCustomObject]@{
          target = $target
          resolver = $resolver
          name = $ans.Name
          type = $ans.Type
          data = $ans.IPAddress
          ttl = $ans.TTL
          ok = $true
        }
      }
    } catch {
      $results += [PSCustomObject]@{
        target = $target
        resolver = $resolver
        ok = $false
        error = $_.Exception.Message
      }
    }
  }
}
$results
"""
    return _ps_run(context, script, parameters={"targets": targets, "resolvers": resolvers}, depth=6)


def external_latency_probe(subject, context: Dict[str, Any], options: Dict[str, Any]):
    inputs = _read_inputs(options)
    targets = inputs.get("targets") or []
    port = int(inputs.get("port") or 443)
    script = r"""
param($targets, $port)
$results = @()
foreach ($target in $targets) {
  if (-not $target) { continue }
  try {
    $res = Test-NetConnection -ComputerName $target -Port $port -InformationLevel Detailed
    $results += [PSCustomObject]@{
      target = $target
      port = $port
      reachable = $res.TcpTestSucceeded
      remote_address = $res.RemoteAddress
      interface = $res.InterfaceAlias
      latency_ms = if ($res.PingSucceeded) { $res.PingReplyDetails.RoundtripTime } else { $null }
    }
  } catch {
    $results += [PSCustomObject]@{
      target = $target
      port = $port
      reachable = $false
      error = $_.Exception.Message
    }
  }
}
$results
"""
    return _ps_run(context, script, parameters={"targets": targets, "port": port}, depth=6)


def build_probe_handlers() -> Dict[str, Any]:
    return {
        "identity.local_system_info": local_system_info_probe,
        "connectivity.local_interfaces": local_interfaces_probe,
        "connectivity.local_routes": local_routes_probe,
        "connectivity.dns_resolve_external": dns_resolve_probe,
        "connectivity.port_probe_external": port_probe,
        "config.firewall_profiles_local": firewall_profiles_probe,
        "health.time.local_status": time_local_status_probe,
        "health.time.dc_offset": time_dc_offset_probe,
        "health.time.ntp_offset": time_ntp_offset_probe,
        "config.certificates.machine_inventory": cert_inventory_probe,
        "connectivity.tls_probe": tls_probe,
        "health.process.inventory": process_inventory_probe,
        "health.service.process_map": service_process_map_probe,
        "health.resources.pressure": resource_pressure_probe,
        "connectivity.network_context": network_context_probe,
        "connectivity.dns.multi_resolver": dns_multi_resolver_probe,
        "connectivity.latency.external_endpoints": external_latency_probe,
        "health.eventlog.summary": eventlog_summary_probe,
        "config.registry.watchlist_snapshot": registry_watchlist_probe,
    }
