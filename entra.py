from microsoft import ServiceClient, PowerShellModuleClient


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


class EntraClient(ServiceClient):
    def __init__(self, graph_session, powershell=None, powershell_options=None):
        super().__init__(graph_session)
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = EntraPowerShellClient(**options)
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

    def list_users(self, top=50, select=None):
        params = {"$top": top}
        if select:
            params["$select"] = ",".join(select) if isinstance(select, (list, tuple)) else select
        response = self.get("/users", params=params)
        return response.json().get("value", [])

    def get_user(self, user_id):
        response = self.get(f"/users/{user_id}")
        return response.json()

    def create_user(self, user_principal_name, display_name, password, mail_nickname=None, account_enabled=True, force_change_password=False):
        payload = {
            "accountEnabled": account_enabled,
            "displayName": display_name,
            "mailNickname": mail_nickname or user_principal_name.split("@")[0],
            "userPrincipalName": user_principal_name,
            "passwordProfile": {
                "forceChangePasswordNextSignIn": force_change_password,
                "password": password,
            },
        }
        response = self.post("/users", json=payload)
        return response.json()

    def update_user(self, user_id, updates):
        response = self.patch(f"/users/{user_id}", json=updates)
        return response.json() if response.content else True

    def delete_user(self, user_id):
        self.delete(f"/users/{user_id}")
        return True

    def list_user_member_of(self, user_id, top=50):
        response = self.get(f"/users/{user_id}/memberOf", params={"$top": top})
        return response.json().get("value", [])

    def list_groups(self, top=50, select=None):
        params = {"$top": top}
        if select:
            params["$select"] = ",".join(select) if isinstance(select, (list, tuple)) else select
        response = self.get("/groups", params=params)
        return response.json().get("value", [])

    def get_group(self, group_id):
        response = self.get(f"/groups/{group_id}")
        return response.json()

    def create_group(self, display_name, mail_nickname, security_enabled=True, mail_enabled=False, group_types=None, description=None):
        payload = {
            "displayName": display_name,
            "mailNickname": mail_nickname,
            "securityEnabled": security_enabled,
            "mailEnabled": mail_enabled,
        }
        if group_types:
            payload["groupTypes"] = group_types
        if description:
            payload["description"] = description
        response = self.post("/groups", json=payload)
        return response.json()

    def update_group(self, group_id, updates):
        response = self.patch(f"/groups/{group_id}", json=updates)
        return response.json() if response.content else True

    def delete_group(self, group_id):
        self.delete(f"/groups/{group_id}")
        return True

    def list_group_members(self, group_id, top=50):
        response = self.get(f"/groups/{group_id}/members", params={"$top": top})
        return response.json().get("value", [])

    def add_group_member(self, group_id, user_id):
        payload = {"@odata.id": f"https://graph.microsoft.com/v1.0/users/{user_id}"}
        response = self.post(f"/groups/{group_id}/members/$ref", json=payload)
        return response.json() if response.content else True

    def remove_group_member(self, group_id, member_id):
        self.delete(f"/groups/{group_id}/members/{member_id}/$ref")
        return True

    def list_applications(self, top=50, select=None):
        params = {"$top": top}
        if select:
            params["$select"] = ",".join(select) if isinstance(select, (list, tuple)) else select
        response = self.get("/applications", params=params)
        return response.json().get("value", [])

    def get_application(self, app_id):
        response = self.get(f"/applications/{app_id}")
        return response.json()

    def list_service_principals(self, top=50, select=None):
        params = {"$top": top}
        if select:
            params["$select"] = ",".join(select) if isinstance(select, (list, tuple)) else select
        response = self.get("/servicePrincipals", params=params)
        return response.json().get("value", [])

    def get_service_principal(self, sp_id):
        response = self.get(f"/servicePrincipals/{sp_id}")
        return response.json()

    def list_users_powershell(self, top=50, **powershell_options):
        cmd = "Get-MgUser" + _ps_params({"Top": top})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def get_user_powershell(self, user_id, **powershell_options):
        cmd = "Get-MgUser" + _ps_params({"UserId": user_id})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_groups_powershell(self, top=50, **powershell_options):
        cmd = "Get-MgGroup" + _ps_params({"Top": top})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def get_group_powershell(self, group_id, **powershell_options):
        cmd = "Get-MgGroup" + _ps_params({"GroupId": group_id})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def set_user_license_powershell(self, user_id, add_sku_ids=None, remove_sku_ids=None, **powershell_options):
        add_block = "$null"
        if add_sku_ids:
            add_block = "@(" + ",".join(f"@{{SkuId = '{_ps_quote(sku)}'}}" for sku in add_sku_ids) + ")"
        remove_block = "@()"
        if remove_sku_ids:
            remove_block = "@(" + ",".join(f"'{_ps_quote(sku)}'" for sku in remove_sku_ids) + ")"
        cmd = (
            f"Set-MgUserLicense -UserId '{_ps_quote(user_id)}' "
            f"-AddLicenses {add_block} -RemoveLicenses {remove_block}"
        )
        return self._get_powershell(**powershell_options).run(cmd)


class EntraPowerShellClient(PowerShellModuleClient):
    def __init__(self, session=None, tenant_id=None, scopes=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.tenant_id = tenant_id
        self.scopes = scopes
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        if self.connect_script:
            return self.connect_script
        cmd = "Import-Module Microsoft.Graph; Connect-MgGraph"
        if self.tenant_id:
            cmd += f" -TenantId '{_ps_quote(self.tenant_id)}'"
        if self.scopes:
            cmd += f" -Scopes {_ps_value(self.scopes)}"
        return cmd

    def _disconnect_script(self):
        return self.disconnect_script or "Disconnect-MgGraph"
