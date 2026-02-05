from microsoft import PowerShellModuleClient, is_powershell_envelope, unwrap_powershell_data


def _ps_quote(value):
    """Internal helper for ps quote."""
    return str(value).replace("'", "''")


def _ps_value(value):
    """Internal helper for ps value."""
    if isinstance(value, bool):
        return "$true" if value else "$false"
    if value is None:
        return "$null"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple, set)):
        return "@(" + ",".join(_ps_value(v) for v in value) + ")"
    return f"'{_ps_quote(value)}'"


def _wrap_envelope(result, payload_builder):
    """Internal helper for wrap envelope."""
    if is_powershell_envelope(result):
        if not result.get("ok", True):
            return result
        data = unwrap_powershell_data(result)
        payload = payload_builder(data)
        return {**result, "data": payload}
    return payload_builder(result)


class LocalEventLogsClient:
    """Client for Local Event Logs operations."""
    def __init__(self, powershell=None, powershell_options=None):
        """Initialize the instance."""
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        """Get powershell."""
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = LocalEventLogsPowerShellClient(**options)
        return self._powershell

    def connect_powershell(self, **options):
        """Run connect powershell."""
        return self._get_powershell(**options).connect()

    def disconnect_powershell(self):
        """Run disconnect powershell."""
        if self._powershell:
            return self._powershell.disconnect()
        return True

    def run_powershell(self, script, **options):
        """Run powershell."""
        return self._get_powershell(**options).run(script)

    def run_powershell_json(self, script, **options):
        """Run powershell json."""
        return self._get_powershell(**options).run_json(script)

    def eventlog_summary(
        self,
        log_names=None,
        levels=None,
        time_window_hours=24,
        event_ids=None,
        providers=None,
        max_events=500,
        computer=None,
        sample_size=10,
    ):
        """Run eventlog summary."""
        script = r"""
param($logNames, $levels, $hours, $eventIds, $providers, $maxEvents, $computer, $sampleSize)
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
    if ($levelMap.ContainsKey($key)) {
      $levelNums += $levelMap[$key]
    }
  }
}
$startTime = $null
if ($hours) {
  $startTime = (Get-Date).AddHours(-1 * [double]$hours)
}
$events = @()
foreach ($logName in ($logNames | Where-Object { $_ -ne $null -and $_ -ne "" })) {
  $filter = @{
    LogName = $logName
  }
  if ($startTime) { $filter.StartTime = $startTime }
  if ($levelNums.Count -gt 0) { $filter.Level = $levelNums }
  if ($eventIds) { $filter.Id = $eventIds }
  if ($providers) { $filter.ProviderName = $providers }
  try {
    if ($computer) {
      $events += Get-WinEvent -FilterHashtable $filter -MaxEvents $maxEvents -ComputerName $computer -ErrorAction Stop
    } else {
      $events += Get-WinEvent -FilterHashtable $filter -MaxEvents $maxEvents -ErrorAction Stop
    }
  } catch {
    # ignore per-log failures, but capture error counts
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
    if (-not $lastError -or $evt.TimeCreated -gt $lastError) {
      $lastError = $evt.TimeCreated
    }
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
  file_path = $filePath
  total_events = $events.Count
  levels = $levelCounts
  top_event_ids = $topIds
  top_providers = $topProviders
  last_error_time = $lastError
  sample_events = $sample
}
"""
        return self._get_powershell().run_json(
            script,
            parameters={
                "logNames": log_names or ["System", "Application"],
                "levels": levels or ["Error", "Warning"],
                "hours": time_window_hours,
                "eventIds": event_ids,
                "providers": providers,
                "maxEvents": int(max_events) if max_events else 500,
                "computer": computer,
                "sampleSize": int(sample_size) if sample_size else 10,
            },
            depth=6,
        )

    def export_evtx(self, log_names=None, output_dir=None):
        """Export evtx."""
        script = r"""
param($logNames, $outputDir)
if (-not $outputDir) {
  $outputDir = Join-Path $env:TEMP ("evtx_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
}
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
$exports = @()
foreach ($logName in ($logNames | Where-Object { $_ -ne $null -and $_ -ne "" })) {
  $safe = $logName -replace '[\\/:*?"<>|]', '_'
  $path = Join-Path $outputDir ($safe + ".evtx")
  try {
    wevtutil epl "$logName" "$path"
    $exports += [PSCustomObject]@{ log_name = $logName; path = $path }
  } catch {
    $exports += [PSCustomObject]@{ log_name = $logName; path = $path; error = $_.Exception.Message }
  }
}
[PSCustomObject]@{
  output_dir = $outputDir
  exports = $exports
}
"""
        return self._get_powershell().run_json(
            script,
            parameters={"logNames": log_names or ["System", "Application"], "outputDir": output_dir},
            depth=6,
        )

    def import_evtx(self, file_path, max_events=500, sample_size=10):
        """Import evtx."""
        if not file_path:
            raise ValueError("file_path is required")
        script = r"""
param($filePath, $maxEvents, $sampleSize)
$events = Get-WinEvent -Path $filePath -MaxEvents $maxEvents -ErrorAction Stop
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
    if (-not $lastError -or $evt.TimeCreated -gt $lastError) {
      $lastError = $evt.TimeCreated
    }
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
        return self._get_powershell().run_json(
            script,
            parameters={
                "filePath": file_path,
                "maxEvents": int(max_events) if max_events else 500,
                "sampleSize": int(sample_size) if sample_size else 10,
            },
            depth=6,
        )


class LocalEventLogsPowerShellClient(PowerShellModuleClient):
    """Client for Local Event Logs Power Shell operations."""
    def __init__(self, session=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        """Initialize the instance."""
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        """Internal helper for connect script."""
        return self.connect_script

    def _disconnect_script(self):
        """Internal helper for disconnect script."""
        return self.disconnect_script
