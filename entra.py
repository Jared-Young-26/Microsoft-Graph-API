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


class EntraClient(ServiceClient):
    """Client for Entra operations."""
    def __init__(self, graph_session, powershell=None, powershell_options=None):
        """Initialize the instance."""
        super().__init__(graph_session)
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        """Get powershell."""
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = EntraPowerShellClient(**options)
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

    def list_users(self, top=50, select=None):
        """List users."""
        params = {"$top": top}
        if select:
            params["$select"] = ",".join(select) if isinstance(select, (list, tuple)) else select
        response = self.get("/users", params=params)
        return response.json().get("value", [])

    def get_user(self, user_id):
        """Get user."""
        response = self.get(f"/users/{user_id}")
        return response.json()

    def create_user(self, user_principal_name, display_name, password, mail_nickname=None, account_enabled=True, force_change_password=False):
        """Create user."""
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
        """Update user."""
        response = self.patch(f"/users/{user_id}", json=updates)
        return response.json() if response.content else True

    def delete_user(self, user_id):
        """Delete user."""
        self.delete(f"/users/{user_id}")
        return True

    def list_user_member_of(self, user_id, top=50):
        """List user member of."""
        response = self.get(f"/users/{user_id}/memberOf", params={"$top": top})
        return response.json().get("value", [])

    def list_groups(self, top=50, select=None):
        """List groups."""
        params = {"$top": top}
        if select:
            params["$select"] = ",".join(select) if isinstance(select, (list, tuple)) else select
        response = self.get("/groups", params=params)
        return response.json().get("value", [])

    def get_group(self, group_id):
        """Get group."""
        response = self.get(f"/groups/{group_id}")
        return response.json()

    def create_group(
        self,
        display_name,
        mail_nickname=None,
        security_enabled=True,
        mail_enabled=False,
        group_types=None,
        description=None,
        visibility=None,
    ):
        """Create group."""
        nickname = mail_nickname or "".join(ch for ch in display_name if ch.isalnum() or ch in ("_", "-"))
        if not nickname:
            nickname = display_name.replace(" ", "")
        payload = {
            "displayName": display_name,
            "mailNickname": nickname,
            "securityEnabled": security_enabled,
            "mailEnabled": mail_enabled,
        }
        if group_types:
            payload["groupTypes"] = group_types
        if description:
            payload["description"] = description
        if visibility:
            payload["visibility"] = visibility
        response = self.post("/groups", json=payload)
        return response.json()

    def update_group(self, group_id, updates):
        """Update group."""
        response = self.patch(f"/groups/{group_id}", json=updates)
        return response.json() if response.content else True

    def delete_group(self, group_id):
        """Delete group."""
        self.delete(f"/groups/{group_id}")
        return True

    def list_group_members(self, group_id, top=50):
        """List group members."""
        response = self.get(f"/groups/{group_id}/members", params={"$top": top})
        return response.json().get("value", [])

    def add_group_member(self, group_id, user_id):
        """Add group member."""
        payload = {"@odata.id": f"https://graph.microsoft.com/v1.0/users/{user_id}"}
        response = self.post(f"/groups/{group_id}/members/$ref", json=payload)
        return response.json() if response.content else True

    def remove_group_member(self, group_id, member_id):
        """Remove group member."""
        self.delete(f"/groups/{group_id}/members/{member_id}/$ref")
        return True

    def list_applications(self, top=50, select=None):
        """List applications."""
        params = {"$top": top}
        if select:
            params["$select"] = ",".join(select) if isinstance(select, (list, tuple)) else select
        response = self.get("/applications", params=params)
        return response.json().get("value", [])

    def get_application(self, app_id):
        """Get application."""
        response = self.get(f"/applications/{app_id}")
        return response.json()

    def list_service_principals(self, top=50, select=None):
        """List service principals."""
        params = {"$top": top}
        if select:
            params["$select"] = ",".join(select) if isinstance(select, (list, tuple)) else select
        response = self.get("/servicePrincipals", params=params)
        return response.json().get("value", [])

    def get_service_principal(self, sp_id):
        """Get service principal."""
        response = self.get(f"/servicePrincipals/{sp_id}")
        return response.json()

    def list_role_definitions(self, top=50, select=None):
        """List role definitions."""
        params = {"$top": top}
        if select:
            params["$select"] = ",".join(select) if isinstance(select, (list, tuple)) else select
        response = self.get("/roleManagement/directory/roleDefinitions", params=params)
        return response.json().get("value", [])

    def list_role_assignments(self, top=50, principal_id=None, role_definition_id=None, directory_scope_id=None):
        """List role assignments."""
        params = {"$top": top}
        filters = []
        if principal_id:
            filters.append(f"principalId eq '{principal_id}'")
        if role_definition_id:
            filters.append(f"roleDefinitionId eq '{role_definition_id}'")
        if directory_scope_id:
            filters.append(f"directoryScopeId eq '{directory_scope_id}'")
        if filters:
            params["$filter"] = " and ".join(filters)
        response = self.get("/roleManagement/directory/roleAssignments", params=params)
        return response.json().get("value", [])

    def assign_role(self, principal_id, role_definition_id, directory_scope_id="/"):
        """Run assign role."""
        payload = {
            "principalId": principal_id,
            "roleDefinitionId": role_definition_id,
            "directoryScopeId": directory_scope_id,
        }
        response = self.post("/roleManagement/directory/roleAssignments", json=payload)
        return response.json()

    def remove_role_assignment(self, role_assignment_id):
        """Remove role assignment."""
        self.delete(f"/roleManagement/directory/roleAssignments/{role_assignment_id}")
        return True

    def create_application(self, display_name, sign_in_audience="AzureADMyOrg", owners=None, notes=None):
        """Create application."""
        payload = {"displayName": display_name, "signInAudience": sign_in_audience}
        if notes:
            payload["notes"] = notes
        response = self.post("/applications", json=payload)
        app = response.json()
        if owners:
            for owner_id in owners:
                owner_payload = {"@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{owner_id}"}
                self.post(f"/applications/{app.get('id')}/owners/$ref", json=owner_payload)
        return app

    def update_application(self, app_id, updates=None, display_name=None, sign_in_audience=None, notes=None):
        """Update application."""
        payload = {}
        if updates:
            payload.update(updates)
        if display_name is not None:
            payload["displayName"] = display_name
        if sign_in_audience is not None:
            payload["signInAudience"] = sign_in_audience
        if notes is not None:
            payload["notes"] = notes
        response = self.patch(f"/applications/{app_id}", json=payload)
        return response.json() if response.content else True

    def delete_application(self, app_id):
        """Delete application."""
        self.delete(f"/applications/{app_id}")
        return True

    def create_service_principal(self, app_id):
        """Create service principal."""
        payload = {"appId": app_id}
        response = self.post("/servicePrincipals", json=payload)
        return response.json()

    def list_users_powershell(self, top=50, **powershell_options):
        """List users powershell."""
        cmd = "Get-MgUser" + _ps_params({"Top": top})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def get_user_powershell(self, user_id, **powershell_options):
        """Get user powershell."""
        cmd = "Get-MgUser" + _ps_params({"UserId": user_id})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_groups_powershell(self, top=50, **powershell_options):
        """List groups powershell."""
        cmd = "Get-MgGroup" + _ps_params({"Top": top})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def get_group_powershell(self, group_id, **powershell_options):
        """Get group powershell."""
        cmd = "Get-MgGroup" + _ps_params({"GroupId": group_id})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def set_user_license_powershell(self, user_id, add_sku_ids=None, remove_sku_ids=None, **powershell_options):
        """Set user license powershell."""
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
    """Client for Entra Power Shell operations."""
    def __init__(self, session=None, tenant_id=None, scopes=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        """Initialize the instance."""
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.tenant_id = tenant_id
        self.scopes = scopes
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        """Internal helper for connect script."""
        if self.connect_script:
            return self.connect_script
        cmd = "Import-Module Microsoft.Graph; Connect-MgGraph"
        if self.tenant_id:
            cmd += f" -TenantId '{_ps_quote(self.tenant_id)}'"
        if self.scopes:
            cmd += f" -Scopes {_ps_value(self.scopes)}"
        return cmd

    def _disconnect_script(self):
        """Internal helper for disconnect script."""
        return self.disconnect_script or "Disconnect-MgGraph"
