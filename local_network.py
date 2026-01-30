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


def _ps_params(params):
    parts = []
    for key, value in params.items():
        if value is None:
            continue
        parts.append(f"-{key} {_ps_value(value)}")
    return " " + " ".join(parts) if parts else ""


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

    def ping_host(self, host, count=4, timeout_seconds=2, ipv6=False):
        if not host:
            raise ValueError("Host is required.")
        family = "IPv6" if ipv6 else "IPv4"
        script = f"""
        $target = '{_ps_quote(host)}'
        $count = {int(count)}
        $timeout = {int(timeout_seconds)}
        $results = Test-Connection -TargetName $target -Count $count -TimeoutSeconds $timeout -IPv{family[-1]} -ErrorAction Stop
        $times = $results | Select-Object -ExpandProperty ResponseTime
        $summary = [PSCustomObject]@{{
          Host = $target
          AddressFamily = '{family}'
          Count = $count
          Success = $results.Count
          LossPercent = [math]::Round((1 - ($results.Count / $count)) * 100, 2)
          MinMs = ($times | Measure-Object -Minimum).Minimum
          MaxMs = ($times | Measure-Object -Maximum).Maximum
          AvgMs = [math]::Round(($times | Measure-Object -Average).Average, 2)
          Addresses = ($results | Select-Object -ExpandProperty Address -Unique)
        }}
        $summary
        """
        return self._get_powershell().run_json(script)


class LocalNetworkPowerShellClient(PowerShellModuleClient):
    def __init__(self, session=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        if self.connect_script:
            return self.connect_script
        return "Import-Module NetAdapter; Import-Module NetTCPIP"

    def _disconnect_script(self):
        return self.disconnect_script
