from microsoft import ServiceClient, PowerShellModuleClient


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


def _ps_params(params):
    """Internal helper for ps params."""
    parts = []
    for key, value in params.items():
        if value is None:
            continue
        parts.append(f"-{key} {_ps_value(value)}")
    return " " + " ".join(parts) if parts else ""


class PurviewClient(ServiceClient):
    """Client for Purview operations."""
    def __init__(self, graph_session, powershell=None, powershell_options=None):
        """Initialize the instance."""
        super().__init__(graph_session)
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        """Get powershell."""
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = PurviewPowerShellClient(**options)
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

    def list_retention_policies_powershell(self, **powershell_options):
        """List retention policies powershell."""
        cmd = "Get-RetentionCompliancePolicy"
        return self._get_powershell(**powershell_options).run_json(cmd)

    def get_retention_policy_powershell(self, name, **powershell_options):
        """Get retention policy powershell."""
        cmd = "Get-RetentionCompliancePolicy" + _ps_params({"Identity": name})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_retention_rules_powershell(self, policy_name=None, **powershell_options):
        """List retention rules powershell."""
        cmd = "Get-RetentionComplianceRule" + _ps_params({"Policy": policy_name})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def get_retention_rule_powershell(self, name, **powershell_options):
        """Get retention rule powershell."""
        cmd = "Get-RetentionComplianceRule" + _ps_params({"Identity": name})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_sensitivity_labels_powershell(self, **powershell_options):
        """List sensitivity labels powershell."""
        cmd = "Get-Label"
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_label_policies_powershell(self, **powershell_options):
        """List label policies powershell."""
        cmd = "Get-LabelPolicy"
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_dlp_policies_powershell(self, **powershell_options):
        """List dlp policies powershell."""
        cmd = "Get-DlpCompliancePolicy"
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_dlp_rules_powershell(self, policy_name=None, **powershell_options):
        """List dlp rules powershell."""
        cmd = "Get-DlpComplianceRule" + _ps_params({"Policy": policy_name})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def get_dlp_policy_powershell(self, name, **powershell_options):
        """Get dlp policy powershell."""
        cmd = "Get-DlpCompliancePolicy" + _ps_params({"Identity": name})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def get_dlp_rule_powershell(self, name, **powershell_options):
        """Get dlp rule powershell."""
        cmd = "Get-DlpComplianceRule" + _ps_params({"Identity": name})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_compliance_searches_powershell(self, **powershell_options):
        """List compliance searches powershell."""
        cmd = "Get-ComplianceSearch"
        return self._get_powershell(**powershell_options).run_json(cmd)

    def get_compliance_search_powershell(self, name, **powershell_options):
        """Get compliance search powershell."""
        cmd = "Get-ComplianceSearch" + _ps_params({"Identity": name})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def create_compliance_search_powershell(
        self,
        name,
        exchange_locations=None,
        sharepoint_locations=None,
        content_match_query=None,
        **powershell_options,
    ):
        """Create compliance search powershell."""
        params = {
            "Name": name,
            "ExchangeLocation": exchange_locations,
            "SharePointLocation": sharepoint_locations,
            "ContentMatchQuery": content_match_query,
        }
        cmd = "New-ComplianceSearch" + _ps_params(params)
        return self._get_powershell(**powershell_options).run_json(cmd)

    def start_compliance_search_powershell(self, name, **powershell_options):
        """Run start compliance search powershell."""
        cmd = "Start-ComplianceSearch" + _ps_params({"Identity": name})
        return self._get_powershell(**powershell_options).run(cmd)

    def stop_compliance_search_powershell(self, name, **powershell_options):
        """Run stop compliance search powershell."""
        cmd = "Stop-ComplianceSearch" + _ps_params({"Identity": name})
        return self._get_powershell(**powershell_options).run(cmd)

    def remove_compliance_search_powershell(self, name, **powershell_options):
        """Remove compliance search powershell."""
        cmd = "Remove-ComplianceSearch" + _ps_params({"Identity": name, "Confirm": False})
        return self._get_powershell(**powershell_options).run(cmd)

    def list_compliance_search_actions_powershell(self, search_name=None, **powershell_options):
        """List compliance search actions powershell."""
        cmd = "Get-ComplianceSearchAction" + _ps_params({"SearchName": search_name})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def get_compliance_search_action_powershell(self, name, **powershell_options):
        """Get compliance search action powershell."""
        cmd = "Get-ComplianceSearchAction" + _ps_params({"Identity": name})
        return self._get_powershell(**powershell_options).run_json(cmd)


class PurviewPowerShellClient(PowerShellModuleClient):
    """Client for Purview Power Shell operations."""
    def __init__(self, session=None, user_principal_name=None, organization=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        """Initialize the instance."""
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.user_principal_name = user_principal_name
        self.organization = organization
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        """Internal helper for connect script."""
        if self.connect_script:
            return self.connect_script
        cmd = "Import-Module ExchangeOnlineManagement; Connect-IPPSSession"
        if self.user_principal_name:
            cmd += f" -UserPrincipalName '{_ps_quote(self.user_principal_name)}'"
        if self.organization:
            cmd += f" -Organization '{_ps_quote(self.organization)}'"
        return cmd

    def _disconnect_script(self):
        """Internal helper for disconnect script."""
        return self.disconnect_script or "Disconnect-ExchangeOnline -Confirm:$false"
