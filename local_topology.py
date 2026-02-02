from datetime import datetime, timezone

from microsoft import PowerShellModuleClient


def _ps_quote(value):
    return str(value).replace("'", "''")


def _ps_value(value):
    if isinstance(value, bool):
        return "$true" if value else "$false"
    if value is None:
        return "$null"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple, set)):
        return "@(" + ",".join(_ps_value(v) for v in value) + ")"
    return f"'{_ps_quote(value)}'"


class LocalTopologyClient:
    def __init__(self, powershell=None, powershell_options=None):
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = LocalTopologyPowerShellClient(**options)
        return self._powershell

    def connect_powershell(self, **options):
        return self._get_powershell(**options).connect()

    def disconnect_powershell(self):
        if self._powershell:
            return self._powershell.disconnect()
        return True

    def run_powershell(self, script, **options):
        return self._get_powershell(**options).run(script)

    def run_powershell_json(self, script, **options):
        return self._get_powershell(**options).run_json(script)

    def list_dhcp_leases(self, dhcp_server=None, scope_ids=None, max_items=None):
        scopes = _ps_value(scope_ids) if scope_ids else "$null"
        server_expr = _ps_value(dhcp_server) if dhcp_server else "$null"
        limit = f"| Select-Object -First {int(max_items)}" if max_items else ""
        script = f"""
        $server = {server_expr}
        $scopeIds = {scopes}
        $leases = @()
        try {{
          if ($scopeIds -ne $null -and $scopeIds.Count -gt 0) {{
            $scopes = $scopeIds
          }} else {{
            if ($server) {{
              $scopes = Get-DhcpServerv4Scope -ComputerName $server | Select-Object -ExpandProperty ScopeId
            }} else {{
              $scopes = Get-DhcpServerv4Scope | Select-Object -ExpandProperty ScopeId
            }}
          }}
          foreach ($scope in $scopes) {{
            try {{
              if ($server) {{
                $leases += Get-DhcpServerv4Lease -ComputerName $server -ScopeId $scope -ErrorAction Stop
              }} else {{
                $leases += Get-DhcpServerv4Lease -ScopeId $scope -ErrorAction Stop
              }}
            }} catch {{
              $leases += [PSCustomObject]@{{ ScopeId = $scope; Error = $_.Exception.Message }}
            }}
          }}
        }} catch {{
          $leases = [PSCustomObject]@{{ Error = $_.Exception.Message }}
        }}
        $leases | Select-Object IPAddress, HostName, ClientId, AddressState, LeaseExpiryTime, ScopeId, Error {limit}
        """
        return self._get_powershell().run_json(script)

    def list_dns_records(self, dns_server=None, zones=None, record_types=None, max_items=None):
        zones_expr = _ps_value(zones) if zones else "$null"
        types_expr = _ps_value(record_types) if record_types else "@('A','AAAA')"
        server_expr = _ps_value(dns_server) if dns_server else "$null"
        limit = f"| Select-Object -First {int(max_items)}" if max_items else ""
        script = f"""
        $server = {server_expr}
        $zones = {zones_expr}
        $types = {types_expr}
        $records = @()
        try {{
          if ($zones -eq $null -or $zones.Count -eq 0) {{
            if ($server) {{
              $zones = Get-DnsServerZone -ComputerName $server | Select-Object -ExpandProperty ZoneName
            }} else {{
              $zones = Get-DnsServerZone | Select-Object -ExpandProperty ZoneName
            }}
          }}
          foreach ($zone in $zones) {{
            foreach ($type in $types) {{
              try {{
                if ($server) {{
                  $records += Get-DnsServerResourceRecord -ComputerName $server -ZoneName $zone -RRType $type -ErrorAction Stop |
                    Select-Object @{{
                      Name = 'Zone'
                      Expression = {{ $zone }}
                    }}, HostName, RecordType, @{{
                      Name = 'RecordData'
                      Expression = {{ ($_.RecordData | ConvertTo-Json -Compress) }}
                    }}
                }} else {{
                  $records += Get-DnsServerResourceRecord -ZoneName $zone -RRType $type -ErrorAction Stop |
                    Select-Object @{{
                      Name = 'Zone'
                      Expression = {{ $zone }}
                    }}, HostName, RecordType, @{{
                      Name = 'RecordData'
                      Expression = {{ ($_.RecordData | ConvertTo-Json -Compress) }}
                    }}
                }}
              }} catch {{
                $records += [PSCustomObject]@{{ Zone = $zone; RecordType = $type; Error = $_.Exception.Message }}
              }}
            }}
          }}
        }} catch {{
          $records = [PSCustomObject]@{{ Error = $_.Exception.Message }}
        }}
        $records {limit}
        """
        return self._get_powershell().run_json(script)

    def list_print_queues(self, print_server=None, max_items=None):
        server_expr = _ps_value(print_server) if print_server else "$null"
        limit = f"| Select-Object -First {int(max_items)}" if max_items else ""
        script = f"""
        $server = {server_expr}
        try {{
          if ($server) {{
            $printers = Get-Printer -ComputerName $server
          }} else {{
            $printers = Get-Printer
          }}
        }} catch {{
          $printers = [PSCustomObject]@{{ Error = $_.Exception.Message }}
        }}
        $printers | Select-Object Name, ShareName, PortName, DriverName, PrinterStatus, Shared, Published, Location, Comment {limit}
        """
        return self._get_powershell().run_json(script)

    def list_print_jobs(self, print_server=None, max_items=None):
        server_expr = _ps_value(print_server) if print_server else "$null"
        limit = f"| Select-Object -First {int(max_items)}" if max_items else ""
        script = f"""
        $server = {server_expr}
        $jobs = @()
        try {{
          if ($server) {{
            $printers = Get-Printer -ComputerName $server
          }} else {{
            $printers = Get-Printer
          }}
          foreach ($p in $printers) {{
            try {{
              if ($server) {{
                $jobs += Get-PrintJob -ComputerName $server -PrinterName $p.Name -ErrorAction Stop
              }} else {{
                $jobs += Get-PrintJob -PrinterName $p.Name -ErrorAction Stop
              }}
            }} catch {{}}
          }}
        }} catch {{
          $jobs = [PSCustomObject]@{{ Error = $_.Exception.Message }}
        }}
        $jobs | Select-Object PrinterName, Submitter, DocumentName, JobStatus, TotalPages, Size, TimeSubmitted {limit}
        """
        return self._get_powershell().run_json(script)

    def list_smb_sessions(self, smb_server=None, max_items=None):
        server_expr = _ps_value(smb_server) if smb_server else "$null"
        limit = f"| Select-Object -First {int(max_items)}" if max_items else ""
        script = f"""
        $server = {server_expr}
        try {{
          if ($server) {{
            $session = New-CimSession -ComputerName $server
            $sessions = Get-SmbSession -CimSession $session
            Remove-CimSession $session
          }} else {{
            $sessions = Get-SmbSession
          }}
        }} catch {{
          $sessions = [PSCustomObject]@{{ Error = $_.Exception.Message }}
        }}
        $sessions | Select-Object ClientComputerName, ClientUserName, NumOpens, SessionId, Dialect, EncryptData {limit}
        """
        return self._get_powershell().run_json(script)

    def collect_topology(
        self,
        dhcp_server=None,
        dns_server=None,
        print_server=None,
        smb_server=None,
        dns_zones=None,
        record_types=None,
        include_print_jobs=False,
        max_items=None,
    ):
        errors = []
        data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "dhcp_server": dhcp_server,
            "dns_server": dns_server,
            "print_server": print_server,
            "smb_server": smb_server,
            "dhcp_leases": None,
            "dns_records": None,
            "printers": None,
            "print_jobs": None,
            "smb_sessions": None,
            "errors": errors,
        }

        try:
            data["dhcp_leases"] = self.list_dhcp_leases(
                dhcp_server=dhcp_server, scope_ids=None, max_items=max_items
            )
        except Exception as exc:
            errors.append({"source": "dhcp", "error": str(exc)})

        try:
            data["dns_records"] = self.list_dns_records(
                dns_server=dns_server, zones=dns_zones, record_types=record_types, max_items=max_items
            )
        except Exception as exc:
            errors.append({"source": "dns", "error": str(exc)})

        try:
            data["printers"] = self.list_print_queues(print_server=print_server, max_items=max_items)
        except Exception as exc:
            errors.append({"source": "printers", "error": str(exc)})

        if include_print_jobs:
            try:
                data["print_jobs"] = self.list_print_jobs(print_server=print_server, max_items=max_items)
            except Exception as exc:
                errors.append({"source": "print_jobs", "error": str(exc)})

        try:
            data["smb_sessions"] = self.list_smb_sessions(smb_server=smb_server, max_items=max_items)
        except Exception as exc:
            errors.append({"source": "smb", "error": str(exc)})

        return data

    def ping_targets(self, targets, count=1, timeout_seconds=2, ipv6=False):
        if not targets:
            raise ValueError("Targets are required.")
        targets_expr = _ps_value(targets)
        count = int(count)
        timeout_seconds = int(timeout_seconds)
        ipv_flag = "-IPv6" if ipv6 else "-IPv4"
        script = f"""
        $targets = {targets_expr}
        $results = @()
        foreach ($t in $targets) {{
          try {{
            $pings = Test-Connection -TargetName $t -Count {count} -TimeoutSeconds {timeout_seconds} {ipv_flag} -ErrorAction Stop
            $times = $pings | Select-Object -ExpandProperty ResponseTime
            $results += [PSCustomObject]@{{
              Target = $t
              Reachable = $true
              Address = ($pings | Select-Object -First 1 -ExpandProperty Address)
              MinMs = ($times | Measure-Object -Minimum).Minimum
              MaxMs = ($times | Measure-Object -Maximum).Maximum
              AvgMs = [math]::Round(($times | Measure-Object -Average).Average, 2)
            }}
          }} catch {{
            $results += [PSCustomObject]@{{
              Target = $t
              Reachable = $false
              Error = $_.Exception.Message
            }}
          }}
        }}
        $results
        """
        return self._get_powershell().run_json(script)


class LocalTopologyPowerShellClient(PowerShellModuleClient):
    def __init__(self, session=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        return self.connect_script

    def _disconnect_script(self):
        return self.disconnect_script
