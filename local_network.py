from microsoft import PowerShellModuleClient, is_powershell_envelope, unwrap_powershell_data


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


def _ps_params(params):
    parts = []
    for key, value in params.items():
        if value is None:
            continue
        parts.append(f"-{key} {_ps_value(value)}")
    return " " + " ".join(parts) if parts else ""


def _wrap_envelope(result, payload_builder):
    if is_powershell_envelope(result):
        if not result.get("ok", True):
            return result
        data = unwrap_powershell_data(result)
        payload = payload_builder(data)
        return {**result, "data": payload}
    return payload_builder(result)


class LocalNetworkClient:
    def __init__(self, powershell=None, powershell_options=None):
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = LocalNetworkPowerShellClient(**options)
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

    def list_adapters(self, name=None, include_hidden=False):
        cmd = "Get-NetAdapter" + _ps_params({"Name": name, "IncludeHidden": include_hidden})
        return self._get_powershell().run_json(cmd)

    def get_adapter_config(self, name):
        cmd = "Get-NetIPConfiguration" + _ps_params({"InterfaceAlias": name})
        return self._get_powershell().run_json(cmd)

    def enable_adapter(self, name):
        cmd = "Enable-NetAdapter" + _ps_params({"Name": name, "Confirm": False})
        return self._get_powershell().run(cmd)

    def disable_adapter(self, name):
        cmd = "Disable-NetAdapter" + _ps_params({"Name": name, "Confirm": False})
        return self._get_powershell().run(cmd)

    def rename_adapter(self, name, new_name):
        cmd = "Rename-NetAdapter" + _ps_params({"Name": name, "NewName": new_name})
        return self._get_powershell().run(cmd)

    def set_dhcp(self, name, enabled=True):
        cmd = "Set-NetIPInterface" + _ps_params({"InterfaceAlias": name, "Dhcp": "Enabled" if enabled else "Disabled"})
        return self._get_powershell().run(cmd)

    def set_static_ipv4(self, name, ip_address, prefix_length, gateway=None, dns_servers=None, remove_existing=False):
        remove_flag = "$true" if remove_existing else "$false"
        dns_list = dns_servers or []
        script = f"""
        $alias = '{_ps_quote(name)}'
        if ({remove_flag}) {{
          Get-NetIPAddress -InterfaceAlias $alias -AddressFamily IPv4 -ErrorAction SilentlyContinue | Remove-NetIPAddress -Confirm:$false
        }}
        New-NetIPAddress -InterfaceAlias $alias -IPAddress '{_ps_quote(ip_address)}' -PrefixLength {int(prefix_length)} {f"-DefaultGateway '{_ps_quote(gateway)}'" if gateway else ""}
        """
        if dns_list:
            script += f"\nSet-DnsClientServerAddress -InterfaceAlias $alias -ServerAddresses {_ps_value(dns_list)}"
        return self._get_powershell().run(script)

    def set_dns_servers(self, name, servers=None, reset=False):
        if reset:
            cmd = "Set-DnsClientServerAddress" + _ps_params({"InterfaceAlias": name, "ResetServerAddresses": True})
            return self._get_powershell().run(cmd)
        if not servers:
            raise ValueError("DNS servers are required unless reset is true.")
        cmd = "Set-DnsClientServerAddress" + _ps_params({"InterfaceAlias": name, "ServerAddresses": servers})
        return self._get_powershell().run(cmd)

    def set_interface_metric(self, name, metric, address_family="IPv4"):
        cmd = "Set-NetIPInterface" + _ps_params(
            {"InterfaceAlias": name, "InterfaceMetric": int(metric), "AddressFamily": address_family}
        )
        return self._get_powershell().run(cmd)

    def set_mtu(self, name, mtu, address_family="IPv4"):
        cmd = "Set-NetIPInterface" + _ps_params(
            {"InterfaceAlias": name, "NlMtuBytes": int(mtu), "AddressFamily": address_family}
        )
        return self._get_powershell().run(cmd)

    def ping_host(self, host=None, hosts=None, count=4, timeout_seconds=2, ipv6=False, parallel=True, throttle=8):
        targets = []
        if hosts:
            if isinstance(hosts, (list, tuple, set)):
                targets = [str(item).strip() for item in hosts if str(item).strip()]
            elif isinstance(hosts, str):
                targets = [part.strip() for part in hosts.split(",") if part.strip()]
        if not targets and host:
            if isinstance(host, str) and "," in host:
                targets = [part.strip() for part in host.split(",") if part.strip()]
            else:
                targets = [str(host).strip()]
        targets = [item for item in targets if item]
        if not targets:
            raise ValueError("Host or hosts are required.")

        family = "IPv6" if ipv6 else "IPv4"
        throttle = int(throttle) if throttle else 8
        script = f"""
        $targets = {_ps_value(targets)}
        $count = {int(count)}
        $timeout = {int(timeout_seconds)}
        $family = '{family}'
        $parallel = {_ps_value(bool(parallel))}
        $throttle = {throttle}

        function Invoke-PingSummary([string]$target) {{
          try {{
            if ($family -eq 'IPv6') {{
              $results = Test-Connection -TargetName $target -Count $count -TimeoutSeconds $timeout -IPv6 -ErrorAction Stop
            }} else {{
              $results = Test-Connection -TargetName $target -Count $count -TimeoutSeconds $timeout -IPv4 -ErrorAction Stop
            }}
            $times = $results | Select-Object -ExpandProperty ResponseTime
            [PSCustomObject]@{{
              Host = $target
              AddressFamily = $family
              Count = $count
              Success = $results.Count
              LossPercent = [math]::Round((1 - ($results.Count / $count)) * 100, 2)
              MinMs = ($times | Measure-Object -Minimum).Minimum
              MaxMs = ($times | Measure-Object -Maximum).Maximum
              AvgMs = [math]::Round(($times | Measure-Object -Average).Average, 2)
              Addresses = ($results | Select-Object -ExpandProperty Address -Unique)
              Error = $null
            }}
          }} catch {{
            [PSCustomObject]@{{
              Host = $target
              AddressFamily = $family
              Count = $count
              Success = 0
              LossPercent = 100
              MinMs = $null
              MaxMs = $null
              AvgMs = $null
              Addresses = @()
              Error = $_.Exception.Message
            }}
          }}
        }}

        if ($targets.Count -le 1 -or -not $parallel) {{
          foreach ($target in $targets) {{
            Invoke-PingSummary -target $target
          }}
        }} else {{
          $targets | ForEach-Object -Parallel {{
            $target = $_
            Invoke-PingSummary -target $target
          }} -ThrottleLimit $throttle
        }}
        """
        return self._get_powershell().run_json(script)

    def resolve_dns_name(self, name, record_type="A", server=None):
        if not name:
            raise ValueError("Name is required.")
        params = {"Name": name, "Type": record_type or "A", "ErrorAction": "Stop"}
        if server:
            params["Server"] = server
        script = f"""
        $params = @{{
          Name = {_ps_value(name)}
          Type = {_ps_value(record_type or "A")}
          ErrorAction = 'Stop'
        }}
        if ({_ps_value(server)}) {{
          $params.Server = {_ps_value(server)}
        }}
        $results = Resolve-DnsName @params
        $answers = foreach ($r in $results) {{
          $answer = $null
          if ($r.IPAddress) {{ $answer = $r.IPAddress }}
          elseif ($r.NameHost) {{ $answer = $r.NameHost }}
          elseif ($r.NameExchange) {{ $answer = $r.NameExchange }}
          elseif ($r.Strings) {{ $answer = ($r.Strings -join '; ') }}
          [PSCustomObject]@{{
            Name = $r.Name
            QueryType = $r.QueryType
            RecordType = $r.Type
            Answer = $answer
            TTL = $r.TTL
            Section = $r.Section
            Server = $r.Server
            NameHost = $r.NameHost
            IPAddress = $r.IPAddress
            NameExchange = $r.NameExchange
            Preference = $r.Preference
          }}
        }}
        $answers
        """
        return self._get_powershell().run_json(script)

    def list_dns_server_records(self, zone, record_type=None, server=None, name_pattern=None, max_results=500):
        if not zone:
            raise ValueError("Zone is required.")
        script = f"""
        $zone = {_ps_value(zone)}
        $rrType = {_ps_value(record_type)}
        $server = {_ps_value(server)}
        $namePattern = {_ps_value(name_pattern)}
        $maxResults = {int(max_results) if max_results else 500}

        $params = @{{
          ZoneName = $zone
          ErrorAction = 'Stop'
        }}
        if ($server) {{
          $params.ComputerName = $server
        }}
        if ($rrType) {{
          $params.RRType = $rrType
        }}

        $records = Get-DnsServerResourceRecord @params
        if ($namePattern) {{
          $records = $records | Where-Object {{
            $_.HostName -like $namePattern -or $_.DistinguishedName -like $namePattern
          }}
        }}
        $total = @($records).Count

        function Get-RecordDataText([object]$record) {{
          if ($null -eq $record.RecordData) {{ return $null }}
          if ($record.RecordData.PSObject.Properties.Match('IPv4Address').Count -gt 0) {{
            return $record.RecordData.IPv4Address.IPAddressToString
          }}
          if ($record.RecordData.PSObject.Properties.Match('IPv6Address').Count -gt 0) {{
            return $record.RecordData.IPv6Address.IPAddressToString
          }}
          if ($record.RecordData.PSObject.Properties.Match('NameServer').Count -gt 0) {{
            return $record.RecordData.NameServer
          }}
          if ($record.RecordData.PSObject.Properties.Match('NameHost').Count -gt 0) {{
            return $record.RecordData.NameHost
          }}
          if ($record.RecordData.PSObject.Properties.Match('PtrDomainName').Count -gt 0) {{
            return $record.RecordData.PtrDomainName
          }}
          if ($record.RecordData.PSObject.Properties.Match('DomainName').Count -gt 0) {{
            return $record.RecordData.DomainName
          }}
          if ($record.RecordData.PSObject.Properties.Match('MailExchange').Count -gt 0) {{
            return $record.RecordData.MailExchange
          }}
          if ($record.RecordData.PSObject.Properties.Match('Text').Count -gt 0) {{
            return ($record.RecordData.Text -join '; ')
          }}
          return ($record.RecordData | Out-String).Trim()
        }}

        $rows = $records | Select-Object -First $maxResults | ForEach-Object {{
          [PSCustomObject]@{{
            zone = $zone
            host_name = $_.HostName
            record_type = $_.RecordType
            ttl = if ($_.TimeToLive) {{ [string]$_.TimeToLive }} else {{ $null }}
            timestamp = $_.Timestamp
            data = Get-RecordDataText $_
            distinguished_name = $_.DistinguishedName
          }}
        }}

        [PSCustomObject]@{{
          zone = $zone
          server = $server
          record_type = $rrType
          name_pattern = $namePattern
          total_count = $total
          returned_count = @($rows).Count
          records = $rows
        }}
        """
        return self._get_powershell().run_json(script)

    def get_dns_client_server_addresses(self, interface_alias=None, address_family=None):
        params = {"ErrorAction": "Stop"}
        if interface_alias:
            params["InterfaceAlias"] = interface_alias
        if address_family:
            params["AddressFamily"] = address_family
        cmd = "Get-DnsClientServerAddress" + _ps_params(params)
        cmd += " | Select-Object InterfaceAlias,InterfaceIndex,AddressFamily,ServerAddresses"
        return self._get_powershell().run_json(cmd)

    def get_dns_client_cache(self, name_pattern=None, max_results=1000):
        script = f"""
        $pattern = {_ps_value(name_pattern)}
        $maxResults = {int(max_results) if max_results else 1000}

        $records = Get-DnsClientCache -ErrorAction Stop
        if ($pattern) {{
          $records = $records | Where-Object {{
            $_.Entry -like $pattern -or $_.Name -like $pattern -or $_.Data -like $pattern
          }}
        }}
        $clientRows = $records | Select-Object Entry,Name,Type,Status,Data,DataLength,Section,TimeToLive
        $normalizedClient = foreach ($row in $clientRows) {{
          [PSCustomObject]@{{
            record_name = $row.Name
            record_type = $row.Type
            data = $row.Data
            ttl = $row.TimeToLive
            section = $row.Section
            source = 'Get-DnsClientCache'
          }}
        }}

        $raw = ipconfig /displaydns 2>&1 | Out-String
        $lines = $raw -split "`r?`n"
        $rows = @()
        $current = @{{}}
        foreach ($line in $lines) {{
          if ($line -match 'Record Name\\s+\\.\\s+:\\s*(.+)$') {{
            if ($current.Count -gt 0) {{
              $rows += [PSCustomObject]$current
              $current = @{{}}
            }}
            $current.record_name = $matches[1].Trim()
            continue
          }}
          if ($line -match 'Record Type\\s+\\.\\s+:\\s*(.+)$') {{
            $current.record_type = $matches[1].Trim()
            continue
          }}
          if ($line -match 'Time To Live\\s+\\.\\s+:\\s*(.+)$') {{
            $current.ttl = $matches[1].Trim()
            continue
          }}
          if ($line -match 'Section\\s+\\.\\s+:\\s*(.+)$') {{
            $current.section = $matches[1].Trim()
            continue
          }}
          if ($line -match 'Record\\s+\\.\\s+:\\s*(.+)$') {{
            $data = $matches[1].Trim()
            if (-not $current.ContainsKey('data')) {{
              $current.data = @()
            }}
            $current.data += $data
            continue
          }}
        }}
        if ($current.Count -gt 0) {{
          $rows += [PSCustomObject]$current
        }}
        $normalizedDisplay = foreach ($row in $rows) {{
          $dataValue = $row.data
          if ($dataValue -is [array]) {{
            $dataValue = $dataValue -join '; '
          }}
          [PSCustomObject]@{{
            record_name = $row.record_name
            record_type = $row.record_type
            data = $dataValue
            ttl = $row.ttl
            section = $row.section
            source = 'ipconfig /displaydns'
          }}
        }}

        $combined = @()
        if ($normalizedClient) {{ $combined += $normalizedClient }}
        if ($normalizedDisplay) {{ $combined += $normalizedDisplay }}
        if ($pattern) {{
          $combined = $combined | Where-Object {{
            $_.record_name -like $pattern -or $_.data -like $pattern -or $_.record_type -like $pattern
          }}
        }}
        $total = @($combined).Count
        $combined = $combined | Select-Object -First $maxResults
        [PSCustomObject]@{{
          total_count = $total
          returned_count = @($combined).Count
          records = $combined
          raw_text = $raw
        }}
        """
        result = self._get_powershell().run_json(script)
        if is_powershell_envelope(result):
            if not result.get("ok", True):
                return result
            payload = unwrap_powershell_data(result) or {}
            records = payload.get("records") or []
            meta = dict(result.get("meta") or {})
            meta["summary"] = {
                "total_count": payload.get("total_count"),
                "returned_count": payload.get("returned_count"),
            }
            if payload.get("raw_text"):
                meta["raw_text"] = payload.get("raw_text")
            return {**result, "data": records, "meta": meta}
        return result

    def get_dns_cache_display(self):
        script = r"""
        $raw = ipconfig /displaydns 2>&1 | Out-String
        $lines = $raw -split "`r?`n"
        $rows = @()
        $current = @{}
        foreach ($line in $lines) {
          if ($line -match 'Record Name\s+\.\s+:\s*(.+)$') {
            if ($current.Count -gt 0) {
              $rows += [PSCustomObject]$current
              $current = @{}
            }
            $current.record_name = $matches[1].Trim()
            continue
          }
          if ($line -match 'Record Type\s+\.\s+:\s*(.+)$') {
            $current.record_type = $matches[1].Trim()
            continue
          }
          if ($line -match 'Time To Live\s+\.\s+:\s*(.+)$') {
            $current.ttl = $matches[1].Trim()
            continue
          }
          if ($line -match 'Data Length\s+\.\s+:\s*(.+)$') {
            $current.data_length = $matches[1].Trim()
            continue
          }
          if ($line -match 'Section\s+\.\s+:\s*(.+)$') {
            $current.section = $matches[1].Trim()
            continue
          }
          if ($line -match 'Record\s+\.\s+:\s*(.+)$') {
            $data = $matches[1].Trim()
            if (-not $current.ContainsKey('data')) {
              $current.data = @()
            }
            $current.data += $data
            continue
          }
        }
        if ($current.Count -gt 0) {
          $rows += [PSCustomObject]$current
        }
        [PSCustomObject]@{
          total_count = @($rows).Count
          records = $rows
          raw_text = $raw
        }
        """
        return self._get_powershell().run_json(script)

    def test_port(self, host, port, information_level="Detailed"):
        if not host or port is None:
            raise ValueError("Host and port are required.")
        level = information_level or "Detailed"
        script = f"""
        $target = '{_ps_quote(host)}'
        $port = {int(port)}
        $level = '{_ps_quote(level)}'
        $result = Test-NetConnection -ComputerName $target -Port $port -InformationLevel $level -ErrorAction Stop
        $latency = $null
        if ($result.PingReplyDetails) {{
          $latency = $result.PingReplyDetails.RoundtripTime
        }}
        $route = $null
        if ($result.TraceRoute) {{
          $route = $result.TraceRoute
        }}
        $interfaceIndex = $null
        if ($result.InterfaceIndex) {{
          $interfaceIndex = $result.InterfaceIndex
        }} elseif ($result.NetAdapter -and $result.NetAdapter.InterfaceIndex) {{
          $interfaceIndex = $result.NetAdapter.InterfaceIndex
        }}
        $interfaceDesc = $null
        if ($result.NetAdapter -and $result.NetAdapter.InterfaceDescription) {{
          $interfaceDesc = $result.NetAdapter.InterfaceDescription
        }}
        [PSCustomObject]@{{
          computer_name = $result.ComputerName
          remote_address = $result.RemoteAddress
          remote_port = $result.RemotePort
          interface_alias = $result.InterfaceAlias
          interface_index = $interfaceIndex
          interface_description = $interfaceDesc
          source_address = $result.SourceAddress
          tcp_test_succeeded = $result.TcpTestSucceeded
          ping_succeeded = $result.PingSucceeded
          ping_latency_ms = $latency
          trace_route = $route
        }}
        """
        return self._get_powershell().run_json(script)

    def trace_route(self, host, max_hops=30, timeout_ms=3000, resolve_names=False):
        if not host:
            raise ValueError("Host is required.")
        resolve_names = bool(resolve_names)
        script = f"""
        $target = '{_ps_quote(host)}'
        $maxHops = {int(max_hops)}
        $timeout = {int(timeout_ms)}
        $resolveNames = {_ps_value(resolve_names)}
        if ($resolveNames) {{
          $raw = tracert -h $maxHops -w $timeout $target 2>&1 | Out-String
        }} else {{
          $raw = tracert -d -h $maxHops -w $timeout $target 2>&1 | Out-String
        }}
        $rows = @()
        $lines = $raw -split "`r?`n"
        foreach ($line in $lines) {{
          if ($line -match '^\s*(\d+)\s+(.+)$') {{
            $hop = [int]$matches[1]
            $rest = $matches[2].Trim()
            if (-not $rest) {{ continue }}

            $timeouts = ([regex]::Matches($rest, '\\*')).Count
            $times = @()
            foreach ($m in [regex]::Matches($rest, '(<\\d+|\\d+)\\s*ms')) {{
              $value = $m.Groups[1].Value
              if ($value.StartsWith('<')) {{ $value = $value.TrimStart('<') }}
              try {{ $times += [int]$value }} catch {{ }}
            }}

            $tail = $rest -replace '(<\\d+|\\d+)\\s*ms', '' -replace '\\*', ''
            $tail = ($tail -replace '\\s+', ' ').Trim()
            $ip = $null
            $name = $null
            if ($tail -match '^(?<name>.+)\\s+\\[(?<ip>[0-9a-fA-F\\.:]+)\\]$') {{
              $name = $matches['name'].Trim()
              $ip = $matches['ip'].Trim()
            }} elseif ($tail -match '^(?<ip>[0-9a-fA-F\\.:]+)$') {{
              $ip = $matches['ip'].Trim()
            }} elseif ($tail) {{
              $name = $tail
            }}

            $avg = $null
            $min = $null
            $max = $null
            if ($times.Count -gt 0) {{
              $avg = [math]::Round(($times | Measure-Object -Average).Average, 2)
              $min = ($times | Measure-Object -Minimum).Minimum
              $max = ($times | Measure-Object -Maximum).Maximum
            }}

            $rows += [PSCustomObject]@{{
              hop = $hop
              address = $ip
              name = $name
              times_ms = $times
              avg_latency_ms = $avg
              min_latency_ms = $min
              max_latency_ms = $max
              timeout_count = $timeouts
            }}
          }}
        }}
        [PSCustomObject]@{{ hops = $rows; raw_text = $raw }}
        """
        result = self._get_powershell().run_json(script)
        if is_powershell_envelope(result):
            if not result.get("ok", True):
                return result
            payload = unwrap_powershell_data(result) or {}
            hops = payload.get("hops") or []
            meta = dict(result.get("meta") or {})
            if payload.get("raw_text"):
                meta["raw_text"] = payload.get("raw_text")
            return {**result, "data": hops, "meta": meta}
        return result

    def pathping_analysis(self, host, max_hops=30, timeout_ms=1000, query_count=1):
        if not host:
            raise ValueError("Host is required.")
        script = f"""
        $target = '{_ps_quote(host)}'
        $maxHops = {int(max_hops)}
        $timeout = {int(timeout_ms)}
        $queries = {int(query_count)}
        $raw = pathping -n -q $queries -p $timeout -w $timeout -h $maxHops $target 2>&1 | Out-String
        $rows = @()
        $lines = $raw -split "`r?`n"
        foreach ($line in $lines) {{
          if ($line -match '^\s*(\d+)\s+([0-9a-fA-F\\.:]+)\\s+(\\d+)\\s*/\\s*(\\d+)\\s*=\\s*(\\d+)%') {{
            $rows += [PSCustomObject]@{{
              hop = [int]$matches[1]
              address = $matches[2]
              loss_percent = [int]$matches[5]
              severity = if ([int]$matches[5] -ge 30) {{ 'high' }} elseif ([int]$matches[5] -ge 10) {{ 'moderate' }} else {{ 'low' }}
            }}
          }}
        }}
        [PSCustomObject]@{{ hops = $rows; raw_text = $raw }}
        """
        result = self._get_powershell().run_json(script)
        if is_powershell_envelope(result):
            if not result.get("ok", True):
                return result
            payload = unwrap_powershell_data(result) or {}
            hops = payload.get("hops") or []
            meta = dict(result.get("meta") or {})
            if payload.get("raw_text"):
                meta["raw_text"] = payload.get("raw_text")
            return {**result, "data": hops, "meta": meta}
        return result

    def get_netstat_connections(self):
        script = r"""
        $raw = netstat -ano 2>&1 | Out-String
        function Split-Address([string]$value) {
          if ($value -match '^\[(.+)\]:(\d+)$') {
            return @{ address = $matches[1]; port = [int]$matches[2] }
          }
          if ($value -match '^(.*):(\d+)$') {
            return @{ address = $matches[1]; port = [int]$matches[2] }
          }
          return @{ address = $value; port = $null }
        }
        $rows = @()
        foreach ($line in ($raw -split "`r?`n")) {
          $trim = $line.Trim()
          if (-not $trim) { continue }
          if ($trim -match '^(TCP)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)$') {
            $local = Split-Address $matches[2]
            $remote = Split-Address $matches[3]
            $rows += [PSCustomObject]@{
              protocol = $matches[1]
              local_address = $local.address
              local_port = $local.port
              remote_address = $remote.address
              remote_port = $remote.port
              state = $matches[4]
              pid = [int]$matches[5]
            }
          } elseif ($trim -match '^(UDP)\s+(\S+)\s+(\S+)\s+(\d+)$') {
            $local = Split-Address $matches[2]
            $remote = Split-Address $matches[3]
            $rows += [PSCustomObject]@{
              protocol = $matches[1]
              local_address = $local.address
              local_port = $local.port
              remote_address = $remote.address
              remote_port = $remote.port
              state = $null
              pid = [int]$matches[4]
            }
          }
        }
        [PSCustomObject]@{ records = $rows; raw_text = $raw }
        """
        return self._get_powershell().run_json(script)

    def get_net_tcp_connections(self, state=None, local_port=None, remote_port=None):
        script = f"""
        $state = {_ps_value(state)}
        $localPort = {_ps_value(local_port)}
        $remotePort = {_ps_value(remote_port)}
        $rows = Get-NetTCPConnection -ErrorAction Stop
        if ($state) {{
          $rows = $rows | Where-Object {{ $_.State -eq $state }}
        }}
        if ($localPort) {{
          $rows = $rows | Where-Object {{ $_.LocalPort -eq $localPort }}
        }}
        if ($remotePort) {{
          $rows = $rows | Where-Object {{ $_.RemotePort -eq $remotePort }}
        }}
        $rows | Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,State,OwningProcess
        """
        return self._get_powershell().run_json(script)

    def list_routes(self, interface_alias=None, address_family=None):
        params = {"ErrorAction": "Stop"}
        if interface_alias:
            params["InterfaceAlias"] = interface_alias
        if address_family:
            params["AddressFamily"] = address_family
        script = f"""
        $routes = Get-NetRoute{_ps_params(params)}
        $rows = foreach ($route in $routes) {{
          $dest = $route.DestinationPrefix
          $isDefault = $dest -eq '0.0.0.0/0' -or $dest -eq '::/0'
          [PSCustomObject]@{{
            destination_prefix = $dest
            next_hop = $route.NextHop
            route_metric = $route.RouteMetric
            interface_alias = $route.InterfaceAlias
            interface_index = $route.InterfaceIndex
            protocol = $route.Protocol
            is_default = $isDefault
          }}
        }}
        $rows
        """
        return self._get_powershell().run_json(script)

    def route_print(self):
        result = self._get_powershell().run("route print")
        return _wrap_envelope(result, lambda output: {"raw_text": output})

    def list_ip_configurations(self, interface_alias=None):
        params = {}
        if interface_alias:
            params["InterfaceAlias"] = interface_alias
        cmd = "Get-NetIPConfiguration" + _ps_params(params)
        cmd += " | Select-Object InterfaceAlias,InterfaceIndex,IPv4Address,IPv6Address,IPv4DefaultGateway,DNSServer"
        return self._get_powershell().run_json(cmd)

    def list_ip_interfaces(self, interface_alias=None, address_family=None):
        params = {"ErrorAction": "Stop"}
        if interface_alias:
            params["InterfaceAlias"] = interface_alias
        if address_family:
            params["AddressFamily"] = address_family
        config_params = dict(params)
        if "AddressFamily" in config_params:
            config_params.pop("AddressFamily", None)
        config_params["ErrorAction"] = "SilentlyContinue"
        script = f"""
        function Join-Values([object]$values, [string]$property) {{
          if ($null -eq $values) {{ return $null }}
          $items = @()
          foreach ($value in $values) {{
            if ($property -and $value.PSObject.Properties.Match($property).Count -gt 0) {{
              $items += $value.$property
            }} elseif ($value) {{
              $items += $value
            }}
          }}
          if ($items.Count -eq 0) {{ return $null }}
          return ($items -join ', ')
        }}

        $configs = Get-NetIPConfiguration{_ps_params(config_params)}
        $configMap = @{{}}
        foreach ($cfg in $configs) {{
          $configMap[$cfg.InterfaceIndex] = $cfg
        }}

        $interfaces = Get-NetIPInterface{_ps_params(params)}
        $rows = foreach ($iface in $interfaces) {{
          $cfg = $configMap[$iface.InterfaceIndex]
          $ipv4 = $null
          $ipv6 = $null
          $gateway = $null
          $dnsServers = $null
          if ($cfg) {{
            $ipv4 = Join-Values $cfg.IPv4Address 'IPAddress'
            $ipv6 = Join-Values $cfg.IPv6Address 'IPAddress'
            $gateway = Join-Values $cfg.IPv4DefaultGateway 'NextHop'
            if ($cfg.DnsServer) {{
              $dnsServers = Join-Values $cfg.DnsServer.ServerAddresses $null
            }}
          }}
          [PSCustomObject]@{{
            interface_alias = $iface.InterfaceAlias
            interface_index = $iface.InterfaceIndex
            address_family = $iface.AddressFamily
            dhcp = $iface.Dhcp
            interface_metric = $iface.InterfaceMetric
            mtu = $iface.NlMtu
            connection_state = $iface.ConnectionState
            ipv4_address = $ipv4
            ipv6_address = $ipv6
            default_gateway = $gateway
            dns_servers = $dnsServers
          }}
        }}
        $rows
        """
        return self._get_powershell().run_json(script)

    def get_adapter_advanced_properties(self, name=None):
        params = {}
        if name:
            params["Name"] = name
        cmd = "Get-NetAdapterAdvancedProperty" + _ps_params(params)
        cmd += " | Select-Object Name,DisplayName,DisplayValue,RegistryKeyword"
        return self._get_powershell().run_json(cmd)

    def list_net_neighbors(self, interface_alias=None, address_family=None):
        params = {}
        if interface_alias:
            params["InterfaceAlias"] = interface_alias
        if address_family:
            params["AddressFamily"] = address_family
        script = f"""
        $neighbors = Get-NetNeighbor{_ps_params(params)}
        $rows = foreach ($row in $neighbors) {{
          [PSCustomObject]@{{
            ip_address = $row.IPAddress
            mac_address = $row.LinkLayerAddress
            state = $row.State
            interface_alias = $row.InterfaceAlias
            address_family = $row.AddressFamily
          }}
        }}
        $rows
        """
        result = self._get_powershell().run_json(script)
        if is_powershell_envelope(result):
            if not result.get("ok", True):
                return result
            data = unwrap_powershell_data(result)
            return {**result, "data": data}
        return result

    def get_arp_table(self):
        script = r"""
        $raw = arp -a 2>&1 | Out-String
        $rows = @()
        foreach ($line in ($raw -split "`r?`n")) {
          if ($line -match '^\s*([0-9\.]+)\s+([0-9a-fA-F:-]+)\s+(\w+)\s*$') {
            $rows += [PSCustomObject]@{
              ip_address = $matches[1]
              mac_address = $matches[2]
              state = $matches[3]
            }
          }
        }
        [PSCustomObject]@{ records = $rows; raw_text = $raw }
        """
        result = self._get_powershell().run_json(script)
        if is_powershell_envelope(result):
            if not result.get("ok", True):
                return result
            payload = unwrap_powershell_data(result) or {}
            records = payload.get("records") or []
            meta = dict(result.get("meta") or {})
            if payload.get("raw_text"):
                meta["raw_text"] = payload.get("raw_text")
            return {**result, "data": records, "meta": meta}
        return result

    def get_firewall_profiles(self):
        cmd = "Get-NetFirewallProfile | Select-Object Name,Enabled,DefaultInboundAction,DefaultOutboundAction,NotifyOnListen"
        return self._get_powershell().run_json(cmd)

    def get_firewall_rules(self, name_pattern=None, direction=None, action=None, enabled=None, profile=None):
        script = f"""
        $pattern = {_ps_value(name_pattern)}
        $direction = {_ps_value(direction)}
        $action = {_ps_value(action)}
        $enabled = {_ps_value(enabled)}
        $profile = {_ps_value(profile)}
        $rules = Get-NetFirewallRule -ErrorAction Stop
        if ($pattern) {{
          $rules = $rules | Where-Object {{ $_.DisplayName -like $pattern -or $_.Name -like $pattern }}
        }}
        if ($direction) {{
          $rules = $rules | Where-Object {{ $_.Direction -eq $direction }}
        }}
        if ($action) {{
          $rules = $rules | Where-Object {{ $_.Action -eq $action }}
        }}
        if ($enabled -ne $null) {{
          $rules = $rules | Where-Object {{ $_.Enabled -eq $enabled }}
        }}
        if ($profile) {{
          $rules = $rules | Where-Object {{ $_.Profile -match $profile }}
        }}
        $rules | Select-Object Name,DisplayName,Direction,Action,Enabled,Profile,PolicyStoreSourceType
        """
        return self._get_powershell().run_json(script)

    def get_firewall_port_filters(self, local_port=None, remote_port=None, protocol=None):
        script = f"""
        $localPort = {_ps_value(local_port)}
        $remotePort = {_ps_value(remote_port)}
        $protocol = {_ps_value(protocol)}
        $filters = Get-NetFirewallPortFilter -ErrorAction Stop
        if ($localPort) {{
          $filters = $filters | Where-Object {{ $_.LocalPort -eq $localPort }}
        }}
        if ($remotePort) {{
          $filters = $filters | Where-Object {{ $_.RemotePort -eq $remotePort }}
        }}
        if ($protocol) {{
          $filters = $filters | Where-Object {{ $_.Protocol -eq $protocol }}
        }}
        $filters | Select-Object LocalPort,RemotePort,Protocol,LocalAddress,RemoteAddress,ICMPType,DynamicTarget
        """
        return self._get_powershell().run_json(script)

    def get_firewall_settings(self):
        cmd = "Get-NetFirewallSetting | Select-Object *"
        return self._get_powershell().run_json(cmd)

    def firewall_quick_check(self, local_port=None, program=None, direction=None, profile=None):
        script = f"""
        $localPort = {_ps_value(local_port)}
        $program = {_ps_value(program)}
        $direction = {_ps_value(direction)}
        $profile = {_ps_value(profile)}

        $profiles = Get-NetFirewallProfile | Select-Object Name,Enabled,DefaultInboundAction,DefaultOutboundAction,NotifyOnListen
        $rules = Get-NetFirewallRule -ErrorAction Stop
        if ($direction) {{
          $rules = $rules | Where-Object {{ $_.Direction -eq $direction }}
        }}
        if ($profile) {{
          $rules = $rules | Where-Object {{ $_.Profile -match $profile }}
        }}

        if ($program) {{
          $rules = $rules | Where-Object {{
            $app = Get-NetFirewallApplicationFilter -AssociatedNetFirewallRule $_
            $app.Program -like $program
          }}
        }}

        if ($localPort) {{
          $rules = $rules | Where-Object {{
            $portFilter = Get-NetFirewallPortFilter -AssociatedNetFirewallRule $_
            ($portFilter.LocalPort -eq $localPort) -or ($portFilter.LocalPort -contains $localPort)
          }}
        }}

        function Join-Values([object]$values) {{
          if ($null -eq $values) {{ return $null }}
          if ($values -is [array]) {{
            return ($values -join ', ')
          }}
          return $values
        }}

        $profileRows = foreach ($profileRow in $profiles) {{
          [PSCustomObject]@{{
            row_type = 'profile'
            profile = $profileRow.Name
            enabled = $profileRow.Enabled
            default_inbound_action = $profileRow.DefaultInboundAction
            default_outbound_action = $profileRow.DefaultOutboundAction
            notify_on_listen = $profileRow.NotifyOnListen
          }}
        }}

        $ruleRows = foreach ($rule in $rules) {{
          $app = Get-NetFirewallApplicationFilter -AssociatedNetFirewallRule $rule
          $portFilter = Get-NetFirewallPortFilter -AssociatedNetFirewallRule $rule
          [PSCustomObject]@{{
            row_type = 'rule'
            name = $rule.Name
            display_name = $rule.DisplayName
            direction = $rule.Direction
            action = $rule.Action
            enabled = $rule.Enabled
            profile = $rule.Profile
            program = $app.Program
            local_port = Join-Values $portFilter.LocalPort
            remote_port = Join-Values $portFilter.RemotePort
            protocol = Join-Values $portFilter.Protocol
          }}
        }}

        $rows = @()
        if ($profileRows) {{ $rows += $profileRows }}
        if ($ruleRows) {{ $rows += $ruleRows }}

        [PSCustomObject]@{{
          profile_count = @($profileRows).Count
          rule_count = @($ruleRows).Count
          rows = $rows
        }}
        """
        result = self._get_powershell().run_json(script)
        if is_powershell_envelope(result):
            if not result.get("ok", True):
                return result
            payload = unwrap_powershell_data(result) or {}
            rows = payload.get("rows") or []
            meta = dict(result.get("meta") or {})
            meta["summary"] = {
                "profile_count": payload.get("profile_count"),
                "rule_count": payload.get("rule_count"),
            }
            return {**result, "data": rows, "meta": meta}
        return result

    def test_smb_path(self, unc_path):
        if not unc_path:
            raise ValueError("UNC path is required.")
        script = f"""
        $path = '{_ps_quote(unc_path)}'
        $exists = Test-Path -Path $path
        [PSCustomObject]@{{ path = $path; exists = $exists }}
        """
        return self._get_powershell().run_json(script)

    def get_smb_connections(self):
        cmd = "Get-SmbConnection | Select-Object ServerName,ShareName,UserName,Credential,NumOpens,Dialect,ContinuouslyAvailable"
        return self._get_powershell().run_json(cmd)

    def get_smb_sessions(self, server=None):
        params = {}
        if server:
            params["ComputerName"] = server
        cmd = "Get-SmbSession" + _ps_params(params)
        cmd += " | Select-Object SessionId,ClientComputerName,ClientUserName,NumOpens,SecondsConnected,Encrypted"
        return self._get_powershell().run_json(cmd)

    def get_smb_open_files(self, server=None):
        params = {}
        if server:
            params["ComputerName"] = server
        cmd = "Get-SmbOpenFile" + _ps_params(params)
        cmd += " | Select-Object ClientComputerName,ClientUserName,ShareRelativePath,SessionId,FileId,Permissions"
        return self._get_powershell().run_json(cmd)

    def get_smb_client_configuration(self):
        cmd = "Get-SmbClientConfiguration | Select-Object EnableSMB1Protocol,EnableSMB2Protocol,EnableSecuritySignature,RequireSecuritySignature,ConnectionCountPerRssNetworkInterface"
        return self._get_powershell().run_json(cmd)

    def smb_status(self, server=None):
        script = f"""
        $server = {_ps_value(server)}
        $connections = Get-SmbConnection | Select-Object ServerName,ShareName,UserName,Credential,NumOpens,Dialect,ContinuouslyAvailable,SessionId

        $sessions = @()
        $sessionError = $null
        try {{
          if ($server) {{
            $sessions = Get-SmbSession -ComputerName $server | Select-Object SessionId,ClientComputerName,ClientUserName,NumOpens,SecondsConnected,Encrypted
          }} else {{
            $sessions = Get-SmbSession | Select-Object SessionId,ClientComputerName,ClientUserName,NumOpens,SecondsConnected,Encrypted
          }}
        }} catch {{
          $sessionError = ($_ | Out-String).Trim()
        }}

        $klist = klist 2>&1 | Out-String
        $whoami = whoami /all 2>&1 | Out-String
        $hasCifs = $klist -match 'cifs/'
        $authHint = if ($hasCifs) {{ 'Kerberos' }} else {{ 'NTLM/Unknown' }}

        $rows = @()
        foreach ($conn in $connections) {{
          $rows += [PSCustomObject]@{{
            row_type = 'connection'
            server = $conn.ServerName
            share = $conn.ShareName
            user = $conn.UserName
            session_id = $conn.SessionId
            dialect = $conn.Dialect
            num_opens = $conn.NumOpens
            continuously_available = $conn.ContinuouslyAvailable
            auth_hint = $authHint
          }}
        }}
        foreach ($sess in $sessions) {{
          $rows += [PSCustomObject]@{{
            row_type = 'session'
            server = $server
            client_computer = $sess.ClientComputerName
            client_user = $sess.ClientUserName
            session_id = $sess.SessionId
            num_opens = $sess.NumOpens
            seconds_connected = $sess.SecondsConnected
            encrypted = $sess.Encrypted
            auth_hint = $authHint
          }}
        }}

        [PSCustomObject]@{{
          rows = $rows
          auth_hint = $authHint
          has_cifs_ticket = $hasCifs
          session_error = $sessionError
          klist_raw = $klist
          whoami_raw = $whoami
        }}
        """
        result = self._get_powershell().run_json(script)
        if is_powershell_envelope(result):
            if not result.get("ok", True):
                return result
            payload = unwrap_powershell_data(result) or {}
            rows = payload.get("rows") or []
            meta = dict(result.get("meta") or {})
            meta["auth_hint"] = payload.get("auth_hint")
            meta["has_cifs_ticket"] = payload.get("has_cifs_ticket")
            if payload.get("session_error"):
                meta["session_error"] = payload.get("session_error")
            if payload.get("klist_raw"):
                meta["klist_raw"] = payload.get("klist_raw")
            if payload.get("whoami_raw"):
                meta["whoami_raw"] = payload.get("whoami_raw")
            return {**result, "data": rows, "meta": meta}
        return result

    def list_net_use(self):
        result = self._get_powershell().run("net use")
        return _wrap_envelope(result, lambda output: {"raw_text": output})

    def list_kerberos_tickets(self):
        result = self._get_powershell().run("klist")
        return _wrap_envelope(result, lambda output: {"raw_text": output})


class LocalNetworkPowerShellClient(PowerShellModuleClient):
    def __init__(self, session=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        if self.connect_script:
            return self.connect_script
        return (
            "Import-Module NetAdapter; "
            "Import-Module NetTCPIP; "
            "Import-Module NetSecurity -ErrorAction SilentlyContinue; "
            "Import-Module DnsServer -ErrorAction SilentlyContinue; "
            "Import-Module SmbShare -ErrorAction SilentlyContinue"
        )

    def _disconnect_script(self):
        return self.disconnect_script
