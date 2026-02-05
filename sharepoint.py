from microsoft import ServiceClient, PowerShellModuleClient
from pathlib import Path


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


class SharePointClient(ServiceClient):
    """Client for Share Point operations."""
    def __init__(self, graph_session, powershell=None, powershell_options=None):
        """Initialize the instance."""
        super().__init__(graph_session)
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        """Get powershell."""
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = SharePointPowerShellClient(**options)
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

    def list_sites(self, search="*"):
        """List sites."""
        response = self.get("/sites", params={"search": search})
        return response.json().get("value", [])

    def get_site(self, site_id):
        """Get site."""
        response = self.get(f"/sites/{site_id}")
        return response.json()

    def list_lists(self, site_id):
        """List lists."""
        response = self.get(f"/sites/{site_id}/lists")
        return response.json().get("value", [])

    def list_list_items(self, site_id, list_id, top=100):
        """List list items."""
        response = self.get(f"/sites/{site_id}/lists/{list_id}/items", params={"$top": top})
        return response.json().get("value", [])

    def get_list_item(self, site_id, list_id, item_id):
        """Get list item."""
        response = self.get(f"/sites/{site_id}/lists/{list_id}/items/{item_id}")
        return response.json()

    def get_site_by_path(self, hostname, site_path):
        """Get site by path."""
        response = self.get(f"/sites/{hostname}:/sites/{site_path}")
        return response.json()

    def list_site_drives(self, site_id):
        """List site drives."""
        response = self.get(f"/sites/{site_id}/drives")
        return response.json().get("value", [])

    def get_site_drive(self, site_id):
        """Get site drive."""
        response = self.get(f"/sites/{site_id}/drive")
        return response.json()

    def list_site_drive_root_items(self, site_id):
        """List site drive root items."""
        response = self.get(f"/sites/{site_id}/drive/root/children")
        return response.json().get("value", [])

    def upload_file_to_site_drive(self, site_id, source_path, parent_folder_id=None):
        """Run upload file to site drive."""
        file_name = Path(source_path).name
        if parent_folder_id:
            url = f"/sites/{site_id}/drive/items/{parent_folder_id}:/{file_name}:/content"
        else:
            url = f"/sites/{site_id}/drive/root:/{file_name}:/content"

        with open(source_path, "rb") as file:
            response = self.put(url, data=file)
        return response.json()

    def list_site_pages(self, site_id):
        """List site pages."""
        response = self.get(f"/sites/{site_id}/pages")
        return response.json().get("value", [])

    def get_page(self, site_id, page_id):
        """Get page."""
        response = self.get(f"/sites/{site_id}/pages/{page_id}")
        return response.json()

    def list_list_columns(self, site_id, list_id):
        """List list columns."""
        response = self.get(f"/sites/{site_id}/lists/{list_id}/columns")
        return response.json().get("value", [])

    def create_list_column(
        self,
        site_id,
        list_id,
        display_name,
        column_type="text",
        required=False,
        description=None,
        default_value=None,
        choices=None,
    ):
        """Create list column."""
        payload = {
            "name": display_name,
            "displayName": display_name,
            "required": bool(required),
        }
        if description:
            payload["description"] = description
        if default_value is not None:
            payload["defaultValue"] = {"value": default_value}

        column_type = (column_type or "text").lower()
        if column_type == "choice":
            choice_list = choices or []
            payload["choice"] = {"choices": list(choice_list), "displayAs": "dropDown"}
        elif column_type == "number":
            payload["number"] = {}
        elif column_type == "boolean":
            payload["boolean"] = {}
        elif column_type == "datetime":
            payload["dateTime"] = {"displayAs": "default"}
        else:
            payload["text"] = {}

        response = self.post(f"/sites/{site_id}/lists/{list_id}/columns", json=payload)
        return response.json()

    def update_list_column(
        self,
        site_id,
        list_id,
        column_id,
        updates=None,
        display_name=None,
        description=None,
        required=None,
        hidden=None,
        default_value=None,
        choices=None,
    ):
        """Update list column."""
        payload = {}
        if updates:
            payload.update(updates)
        if display_name is not None:
            payload["displayName"] = display_name
        if description is not None:
            payload["description"] = description
        if required is not None:
            payload["required"] = bool(required)
        if hidden is not None:
            payload["hidden"] = bool(hidden)
        if default_value is not None:
            payload["defaultValue"] = {"value": default_value}
        if choices is not None:
            payload["choice"] = {"choices": list(choices), "displayAs": "dropDown"}

        response = self.patch(f"/sites/{site_id}/lists/{list_id}/columns/{column_id}", json=payload)
        return response.json()

    def delete_list_column(self, site_id, list_id, column_id):
        """Delete list column."""
        self.delete(f"/sites/{site_id}/lists/{list_id}/columns/{column_id}")
        return True

    def list_site_permissions(self, site_id):
        """List site permissions."""
        response = self.get(f"/sites/{site_id}/permissions")
        return response.json().get("value", [])

    def grant_site_permission(self, site_id, principal_id, principal_type="user", roles=None):
        """Run grant site permission."""
        roles_list = roles or ["read"]
        entry = {}
        if principal_type == "group":
            entry["group"] = {"id": principal_id}
        else:
            entry["user"] = {"id": principal_id}
        payload = {"roles": list(roles_list), "grantedToIdentities": [entry]}
        response = self.post(f"/sites/{site_id}/permissions", json=payload)
        return response.json()

    def delete_site_permission(self, site_id, permission_id):
        """Delete site permission."""
        self.delete(f"/sites/{site_id}/permissions/{permission_id}")
        return True

    def update_site_permission(self, site_id, permission_id, roles=None, updates=None):
        """Update site permission."""
        payload = {}
        if updates:
            payload.update(updates)
        if roles is not None:
            payload["roles"] = list(roles)
        response = self.patch(f"/sites/{site_id}/permissions/{permission_id}", json=payload)
        return response.json() if response.content else True

    def create_list(self, site_id, display_name, columns=None, template="genericList", description=None):
        """Create list."""
        payload = {"displayName": display_name, "list": {"template": template}}
        if description:
            payload["description"] = description
        if columns:
            payload["columns"] = columns
        response = self.post(f"/sites/{site_id}/lists", json=payload)
        return response.json()

    def create_list_item(self, site_id, list_id, fields):
        """Create list item."""
        payload = {"fields": fields}
        response = self.post(f"/sites/{site_id}/lists/{list_id}/items", json=payload)
        return response.json()

    def update_list_item_fields(self, site_id, list_id, item_id, fields):
        """Update list item fields."""
        response = self.patch(f"/sites/{site_id}/lists/{list_id}/items/{item_id}/fields", json=fields)
        return response.json()

    def delete_list_item(self, site_id, list_id, item_id):
        """Delete list item."""
        self.delete(f"/sites/{site_id}/lists/{list_id}/items/{item_id}")
        return True

    def list_sites_powershell(self, include_personal=False, limit="All", filter_query=None, **powershell_options):
        """List sites powershell."""
        params = {"IncludePersonalSite": include_personal, "Limit": limit}
        if filter_query:
            params["Filter"] = filter_query
        cmd = "Get-SPOSite" + _ps_params(params)
        return self._get_powershell(**powershell_options).run_json(cmd)

    def get_site_powershell(self, site_url, **powershell_options):
        """Get site powershell."""
        cmd = "Get-SPOSite" + _ps_params({"Identity": site_url})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def create_site_collection_powershell(
        self,
        url,
        title,
        owner,
        template="STS#3",
        storage_quota=None,
        time_zone_id=None,
        **powershell_options,
    ):
        """Create site collection powershell."""
        params = {
            "Url": url,
            "Title": title,
            "Owner": owner,
            "Template": template,
            "StorageQuota": storage_quota,
            "TimeZoneId": time_zone_id,
        }
        cmd = "New-SPOSite" + _ps_params(params)
        return self._get_powershell(**powershell_options).run_json(cmd)

    def set_site_properties_powershell(self, site_url, **properties):
        """Set site properties powershell."""
        params = {"Identity": site_url}
        params.update(properties)
        cmd = "Set-SPOSite" + _ps_params(params)
        return self._get_powershell().run(cmd)

    def delete_site_collection_powershell(self, site_url, **powershell_options):
        """Delete site collection powershell."""
        cmd = "Remove-SPOSite" + _ps_params({"Identity": site_url, "Confirm": False})
        return self._get_powershell(**powershell_options).run(cmd)

    def restore_deleted_site_powershell(self, site_url, **powershell_options):
        """Run restore deleted site powershell."""
        cmd = "Restore-SPODeletedSite" + _ps_params({"Identity": site_url})
        return self._get_powershell(**powershell_options).run(cmd)

    def list_site_users_powershell(self, site_url, login_name=None, **powershell_options):
        """List site users powershell."""
        params = {"Site": site_url}
        if login_name:
            params["LoginName"] = login_name
        cmd = "Get-SPOUser" + _ps_params(params)
        return self._get_powershell(**powershell_options).run_json(cmd)

    def set_site_user_powershell(self, site_url, login_name, is_site_collection_admin=None, **powershell_options):
        """Set site user powershell."""
        params = {"Site": site_url, "LoginName": login_name, "IsSiteCollectionAdmin": is_site_collection_admin}
        cmd = "Set-SPOUser" + _ps_params(params)
        return self._get_powershell(**powershell_options).run(cmd)


class SharePointPowerShellClient(PowerShellModuleClient):
    """Client for Share Point Power Shell operations."""
    def __init__(self, session=None, admin_url=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        """Initialize the instance."""
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.admin_url = admin_url
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        """Internal helper for connect script."""
        if self.connect_script:
            return self.connect_script
        if not self.admin_url:
            return None
        return (
            "Import-Module Microsoft.Online.SharePoint.PowerShell;"
            f"Connect-SPOService -Url '{_ps_quote(self.admin_url)}'"
        )

    def _disconnect_script(self):
        """Internal helper for disconnect script."""
        return self.disconnect_script
