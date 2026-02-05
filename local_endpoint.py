from microsoft import PowerShellModuleClient, is_powershell_envelope, unwrap_powershell_data


def _ps_quote(value):
    """Internal helper for ps quote."""
    return str(value).replace("'", "''")


def _parse_gpresult_summary(text):
    """Parse gpresult summary."""
    summary = {"user": {}, "computer": {}, "applied_gpos": {"user": [], "computer": []}}
    section = None
    collecting = False
    for line in str(text or "").splitlines():
        stripped = line.strip()
        if not stripped:
            if collecting:
                collecting = False
            continue
        lower = stripped.lower()
        if lower.startswith("computer settings"):
            section = "computer"
            collecting = False
            continue
        if lower.startswith("user settings"):
            section = "user"
            collecting = False
            continue
        if "applied group policy objects" in lower:
            collecting = True
            continue
        if collecting and section:
            if lower.startswith("the following gpos were not applied"):
                collecting = False
                continue
            summary["applied_gpos"][section].append(stripped)
            continue
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            mapped = None
            if key.lower().startswith("domain name"):
                mapped = "domain"
            elif key.lower().startswith("computer name"):
                mapped = "computer_name"
            elif key.lower().startswith("user name"):
                mapped = "user_name"
            elif key.lower().startswith("last time group policy was applied"):
                mapped = "last_applied"
            elif key.lower().startswith("group policy was applied from"):
                mapped = "applied_from"
            if mapped and section:
                summary[section][mapped] = value
    return summary


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


def _ps_params(params):
    """Internal helper for ps params."""
    parts = []
    for key, value in (params or {}).items():
        if value is None:
            continue
        parts.append(f"-{key} {_ps_value(value)}")
    return " " + " ".join(parts) if parts else ""


def _wrap_envelope(result, payload_builder):
    """Internal helper for wrap envelope."""
    if is_powershell_envelope(result):
        if not result.get("ok", True):
            return result
        data = unwrap_powershell_data(result)
        payload = payload_builder(data)
        return {**result, "data": payload}
    return payload_builder(result)


class LocalEndpointClient:
    """Client for Local Endpoint operations."""
    def __init__(self, powershell=None, powershell_options=None):
        """Initialize the instance."""
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        """Get powershell."""
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = LocalEndpointPowerShellClient(**options)
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

    def get_computer_info(self):
        """Get computer info."""
        cmd = (
            "Get-ComputerInfo | Select-Object CsName,CsDomain,CsDomainRole,CsManufacturer,CsModel,"
            "CsSystemType,CsTotalPhysicalMemory,CsNumberOfLogicalProcessors,OsName,OsVersion,OsBuildNumber,"
            "OsArchitecture,OsLastBootUpTime,WindowsProductName,WindowsVersion"
        )
        return self._get_powershell().run_json(cmd)

    def get_cim_summary(self):
        """Get cim summary."""
        script = """
        $cs = Get-CimInstance Win32_ComputerSystem | Select-Object Name,Domain,Manufacturer,Model,TotalPhysicalMemory,NumberOfLogicalProcessors
        $os = Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,LastBootUpTime,InstallDate,OSArchitecture
        $bios = Get-CimInstance Win32_BIOS | Select-Object Manufacturer,SMBIOSBIOSVersion,SerialNumber,ReleaseDate
        [PSCustomObject]@{
          computer_system = $cs
          operating_system = $os
          bios = $bios
        }
        """
        return self._get_powershell().run_json(script)

    def get_systeminfo(self):
        """Get systeminfo."""
        script = r"""
        $raw = systeminfo 2>&1 | Out-String
        $rows = @{}
        foreach ($line in ($raw -split "`r?`n")) {
          if ($line -match '^\s*([^:]+):\s*(.*)$') {
            $key = $matches[1].Trim()
            $val = $matches[2].Trim()
            if ($rows.ContainsKey($key)) {
              if (-not ($rows[$key] -is [System.Collections.ArrayList])) {
                $rows[$key] = [System.Collections.ArrayList]@($rows[$key])
              }
              $null = $rows[$key].Add($val)
            } else {
              $rows[$key] = $val
            }
          }
        }
        [PSCustomObject]@{
          parsed = $rows
          raw_text = $raw
        }
        """
        return self._get_powershell().run_json(script)

    def get_system_inventory(self):
        """Aggregate system inventory with uptime + domain join context."""
        script = r"""
        $cs = Get-CimInstance Win32_ComputerSystem | Select-Object Name,Domain,DomainRole,Manufacturer,Model,TotalPhysicalMemory,NumberOfLogicalProcessors
        $os = Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,LastBootUpTime,InstallDate,OSArchitecture
        $cpu = Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed
        $memoryGb = if ($cs.TotalPhysicalMemory) { [math]::Round($cs.TotalPhysicalMemory / 1GB, 2) } else { $null }
        $uptimeSeconds = $null
        if ($os.LastBootUpTime) {
          try { $uptimeSeconds = [math]::Round(((Get-Date) - $os.LastBootUpTime).TotalSeconds, 0) } catch { $uptimeSeconds = $null }
        }
        [PSCustomObject]@{
          computer_name = $cs.Name
          domain = $cs.Domain
          domain_role = $cs.DomainRole
          domain_joined = ($cs.Domain -ne $null -and $cs.Domain -ne '')
          manufacturer = $cs.Manufacturer
          model = $cs.Model
          total_memory_gb = $memoryGb
          logical_processors = $cs.NumberOfLogicalProcessors
          os_name = $os.Caption
          os_version = $os.Version
          os_build = $os.BuildNumber
          os_architecture = $os.OSArchitecture
          last_boot = $os.LastBootUpTime
          uptime_seconds = $uptimeSeconds
          cpu_name = if ($cpu) { ($cpu | Select-Object -First 1).Name } else { $null }
          cpu_cores = if ($cpu) { ($cpu | Measure-Object -Property NumberOfCores -Sum).Sum } else { $null }
          cpu_logical = if ($cpu) { ($cpu | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum } else { $null }
        }
        """
        return self._get_powershell().run_json(script)

    def list_processes(self, top=25):
        """List processes."""
        script = f"""
        $count = {int(top)}
        $rows = Get-Process | Sort-Object CPU -Descending | Select-Object -First $count Name,Id,CPU,WS,StartTime
        $rows | ForEach-Object {{
          [PSCustomObject]@{{
            name = $_.Name
            id = $_.Id
            cpu = $_.CPU
            memory_bytes = $_.WS
            memory_mb = if ($_.WS) {{ [math]::Round($_.WS / 1MB, 2) }} else {{ $null }}
            start_time = $_.StartTime
          }}
        }}
        """
        return self._get_powershell().run_json(script)

    def list_services(self, name=None, status=None):
        """List services."""
        params = {}
        if name:
            params["Name"] = name
        cmd = "Get-Service" + _ps_params(params)
        if status:
            cmd += f" | Where-Object {{ $_.Status -eq '{_ps_quote(status)}' }}"
        cmd += " | Select-Object Name,DisplayName,Status,StartType,CanStop,ServiceType"
        return self._get_powershell().run_json(cmd)

    def query_event_logs(
        self,
        log_name="System",
        provider=None,
        level=None,
        start_time=None,
        end_time=None,
        event_ids=None,
        max_events=50,
        contains=None,
    ):
        """Run query event logs."""
        script = f"""
        $filter = @{{}}
        $logName = {_ps_value(log_name)}
        if ($logName) {{ $filter.LogName = $logName }}
        $provider = {_ps_value(provider)}
        if ($provider) {{ $filter.ProviderName = $provider }}
        $level = {_ps_value(level)}
        if ($level) {{ $filter.Level = [int]$level }}
        $eventIds = {_ps_value(event_ids)}
        if ($eventIds) {{ $filter.Id = $eventIds }}
        $startTime = {_ps_value(start_time)}
        if ($startTime) {{ $filter.StartTime = (Get-Date $startTime) }}
        $endTime = {_ps_value(end_time)}
        if ($endTime) {{ $filter.EndTime = (Get-Date $endTime) }}
        $maxEvents = {int(max_events) if max_events else 50}
        $events = Get-WinEvent -FilterHashtable $filter -MaxEvents $maxEvents -ErrorAction Stop
        $needle = {_ps_value(contains)}
        if ($needle) {{
          $events = $events | Where-Object {{ $_.Message -like "*$needle*" }}
        }}
        $events | ForEach-Object {{
          $msg = $_.Message
          if ($msg -and $msg.Length -gt 300) {{
            $msg = $msg.Substring(0, 300) + "..."
          }}
          [PSCustomObject]@{{
            time_created = $_.TimeCreated
            event_id = $_.Id
            level = $_.LevelDisplayName
            provider = $_.ProviderName
            machine = $_.MachineName
            message = $msg
          }}
        }}
        """
        return self._get_powershell().run_json(script)

    def wevtutil_query(self, log_name="System", query=None, max_events=50):
        """Run wevtutil query."""
        if not log_name:
            raise ValueError("Log name is required.")
        query_fragment = f'/q:"{_ps_quote(query)}"' if query else ""
        cmd = f'wevtutil qe "{_ps_quote(log_name)}" {query_fragment} /f:text /c:{int(max_events)}'
        result = self._get_powershell().run(cmd)
        return _wrap_envelope(result, lambda output: {"raw_text": output})

    def legacy_event_log(self, log_name="System", source=None, entry_type=None, after=None, before=None, max_events=50):
        """Run legacy event log."""
        params = {"LogName": log_name, "Newest": int(max_events)}
        if source:
            params["Source"] = source
        if entry_type:
            params["EntryType"] = entry_type
        cmd = "Get-EventLog" + _ps_params(params)
        if after:
            cmd += f" | Where-Object {{ $_.TimeGenerated -ge (Get-Date {_ps_value(after)}) }}"
        if before:
            cmd += f" | Where-Object {{ $_.TimeGenerated -le (Get-Date {_ps_value(before)}) }}"
        cmd += " | Select-Object TimeGenerated,EntryType,Source,EventID,Message,MachineName"
        return self._get_powershell().run_json(cmd)

    def list_hotfixes(self):
        """List hotfixes."""
        cmd = "Get-HotFix | Select-Object HotFixID,Description,InstalledOn,InstalledBy"
        return self._get_powershell().run_json(cmd)

    def list_dism_packages(self):
        """List dism packages."""
        result = self._get_powershell().run("DISM /Online /Get-Packages")
        return _wrap_envelope(result, lambda output: {"raw_text": output})

    def whoami_all(self):
        """Run whoami all."""
        result = self._get_powershell().run("whoami /all")
        return _wrap_envelope(result, lambda output: {"raw_text": output})

    def gpresult_report(self, report_type="summary", output_path=None, include_summary=False):
        """Run gpresult report."""
        report_type = (report_type or "summary").lower()
        if report_type in {"html", "h"}:
            script = f"""
            $path = {_ps_value(output_path)}
            if (-not $path) {{
              $path = Join-Path $env:TEMP ("gpresult_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".html")
            }}
            gpresult /h $path /f | Out-String | Out-Null
            [PSCustomObject]@{{ report_path = $path; report_type = 'html' }}
            """
            result = self._get_powershell().run_json(script)
            if include_summary and is_powershell_envelope(result) and result.get("ok", True):
                summary_result = self._get_powershell().run("gpresult /r")
                if is_powershell_envelope(summary_result) and summary_result.get("ok", True):
                    raw = unwrap_powershell_data(summary_result)
                    summary = _parse_gpresult_summary(raw)
                    payload = unwrap_powershell_data(result) or {}
                    payload["summary"] = summary
                    return {**result, "data": payload}
            return result
        result = self._get_powershell().run("gpresult /r")
        wrapped = _wrap_envelope(result, lambda output: {"raw_text": output, "report_type": "summary"})
        if include_summary and is_powershell_envelope(wrapped) and wrapped.get("ok", True):
            raw = unwrap_powershell_data(wrapped).get("raw_text")
            summary = _parse_gpresult_summary(raw)
            payload = unwrap_powershell_data(wrapped) or {}
            payload["summary"] = summary
            return {**wrapped, "data": payload}
        return wrapped

    def gpresultant_set_of_policy(self, report_path=None):
        """Run gpresultant set of policy."""
        script = f"""
        $path = {_ps_value(report_path)}
        if (-not $path) {{
          $path = Join-Path $env:TEMP ("rsop_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".html")
        }}
        Get-GPResultantSetOfPolicy -ReportType Html -Path $path
        [PSCustomObject]@{{ report_path = $path }}
        """
        return self._get_powershell().run_json(script)


class LocalEndpointPowerShellClient(PowerShellModuleClient):
    """Client for Local Endpoint Power Shell operations."""
    def __init__(self, session=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        """Initialize the instance."""
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        """Internal helper for connect script."""
        if self.connect_script:
            return self.connect_script
        return "Import-Module GroupPolicy -ErrorAction SilentlyContinue"

    def _disconnect_script(self):
        """Internal helper for disconnect script."""
        return self.disconnect_script
