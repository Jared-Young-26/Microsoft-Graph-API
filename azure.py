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


class AzureClient(ServiceClient):
    """Client for Azure operations."""
    def __init__(self, graph_session, powershell=None, powershell_options=None):
        """Initialize the instance."""
        super().__init__(graph_session)
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        """Get powershell."""
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = AzurePowerShellClient(**options)
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

    def list_subscriptions_powershell(self, **powershell_options):
        """List subscriptions powershell."""
        cmd = "Get-AzSubscription"
        return self._get_powershell(**powershell_options).run_json(cmd)

    def set_subscription_context_powershell(self, subscription_id, **powershell_options):
        """Set subscription context powershell."""
        cmd = "Set-AzContext" + _ps_params({"SubscriptionId": subscription_id})
        return self._get_powershell(**powershell_options).run(cmd)

    def list_resource_groups_powershell(self, **powershell_options):
        """List resource groups powershell."""
        cmd = "Get-AzResourceGroup"
        return self._get_powershell(**powershell_options).run_json(cmd)

    def get_resource_group_powershell(self, name, **powershell_options):
        """Get resource group powershell."""
        cmd = "Get-AzResourceGroup" + _ps_params({"Name": name})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def create_resource_group_powershell(self, name, location, **powershell_options):
        """Create resource group powershell."""
        cmd = "New-AzResourceGroup" + _ps_params({"Name": name, "Location": location})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def delete_resource_group_powershell(self, name, force=True, **powershell_options):
        """Delete resource group powershell."""
        cmd = "Remove-AzResourceGroup" + _ps_params({"Name": name, "Force": force, "Confirm": False})
        return self._get_powershell(**powershell_options).run(cmd)

    def list_resources_powershell(self, resource_group=None, **powershell_options):
        """List resources powershell."""
        cmd = "Get-AzResource" + _ps_params({"ResourceGroupName": resource_group})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_storage_accounts_powershell(self, resource_group=None, **powershell_options):
        """List storage accounts powershell."""
        cmd = "Get-AzStorageAccount" + _ps_params({"ResourceGroupName": resource_group})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_virtual_machines_powershell(self, resource_group=None, status=False, **powershell_options):
        """List virtual machines powershell."""
        cmd = "Get-AzVM" + _ps_params({"ResourceGroupName": resource_group, "Status": status})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_virtual_networks_powershell(self, resource_group=None, **powershell_options):
        """List virtual networks powershell."""
        cmd = "Get-AzVirtualNetwork" + _ps_params({"ResourceGroupName": resource_group})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_role_assignments_powershell(self, scope=None, **powershell_options):
        """List role assignments powershell."""
        cmd = "Get-AzRoleAssignment" + _ps_params({"Scope": scope})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_key_vaults_powershell(self, resource_group=None, **powershell_options):
        """List key vaults powershell."""
        cmd = "Get-AzKeyVault" + _ps_params({"ResourceGroupName": resource_group})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def get_key_vault_powershell(self, name, resource_group=None, **powershell_options):
        """Get key vault powershell."""
        cmd = "Get-AzKeyVault" + _ps_params({"VaultName": name, "ResourceGroupName": resource_group})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_key_vault_secrets_powershell(self, vault_name, **powershell_options):
        """List key vault secrets powershell."""
        cmd = "Get-AzKeyVaultSecret" + _ps_params({"VaultName": vault_name})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_app_services_powershell(self, resource_group=None, **powershell_options):
        """List app services powershell."""
        cmd = "Get-AzWebApp" + _ps_params({"ResourceGroupName": resource_group})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_function_apps_powershell(self, resource_group=None, **powershell_options):
        """List function apps powershell."""
        cmd = "Get-AzFunctionApp" + _ps_params({"ResourceGroupName": resource_group})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_sql_servers_powershell(self, resource_group=None, **powershell_options):
        """List sql servers powershell."""
        cmd = "Get-AzSqlServer" + _ps_params({"ResourceGroupName": resource_group})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_sql_databases_powershell(self, resource_group, server_name, **powershell_options):
        """List sql databases powershell."""
        cmd = "Get-AzSqlDatabase" + _ps_params({"ResourceGroupName": resource_group, "ServerName": server_name})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_cosmos_accounts_powershell(self, resource_group=None, **powershell_options):
        """List cosmos accounts powershell."""
        cmd = "Get-AzCosmosDBAccount" + _ps_params({"ResourceGroupName": resource_group})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_network_interfaces_powershell(self, resource_group=None, **powershell_options):
        """List network interfaces powershell."""
        cmd = "Get-AzNetworkInterface" + _ps_params({"ResourceGroupName": resource_group})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_public_ip_addresses_powershell(self, resource_group=None, **powershell_options):
        """List public ip addresses powershell."""
        cmd = "Get-AzPublicIpAddress" + _ps_params({"ResourceGroupName": resource_group})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_disks_powershell(self, resource_group=None, **powershell_options):
        """List disks powershell."""
        cmd = "Get-AzDisk" + _ps_params({"ResourceGroupName": resource_group})
        return self._get_powershell(**powershell_options).run_json(cmd)


class AzurePowerShellClient(PowerShellModuleClient):
    """Client for Azure Power Shell operations."""
    def __init__(self, session=None, tenant_id=None, subscription_id=None, auth_mode="interactive", connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        """Initialize the instance."""
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.tenant_id = tenant_id
        self.subscription_id = subscription_id
        self.auth_mode = auth_mode
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        """Internal helper for connect script."""
        if self.connect_script:
            return self.connect_script
        cmd = "Import-Module Az.Accounts; Connect-AzAccount"
        if self.auth_mode == "device":
            cmd += " -UseDeviceAuthentication"
        if self.tenant_id:
            cmd += f" -TenantId '{_ps_quote(self.tenant_id)}'"
        if self.subscription_id:
            cmd += f"; Set-AzContext -SubscriptionId '{_ps_quote(self.subscription_id)}'"
        return cmd

    def _disconnect_script(self):
        """Internal helper for disconnect script."""
        return self.disconnect_script or "Disconnect-AzAccount -Confirm:$false"
