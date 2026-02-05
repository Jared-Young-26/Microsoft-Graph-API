from microsoft import ServiceClient, PowerShellModuleClient
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from urllib.parse import quote
import os

load_dotenv()


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


class OneDriveClient(ServiceClient):
    """Client for One Drive operations."""
    def __init__(self, graph_session, drive_id, powershell=None, powershell_options=None):
        """Initialize the instance."""
        super().__init__(graph_session)
        self._powershell = powershell
        self._powershell_options = powershell_options or {}
        self.drive_id = drive_id
        self.account_id = os.getenv("ONEDRIVE_ACCOUNT_ID")
        self.account_upn = os.getenv("ONEDRIVE_ACCOUNT_UPN")

    def _get_powershell(self, **overrides):
        """Get powershell."""
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = OneDrivePowerShellClient(**options)
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

    def list_drives(self, user_id="me"):
        """List drives."""
        url = f"/users/{user_id}/drives" if user_id != "me" else "/me/drives"
        response = self.get(url)
        return response.json().get("value", [])

    def get_user_drive_id(self, user_id):
        """Get user drive id."""
        safe_user_id = quote(str(user_id), safe="")
        response = self.get(
            f"/users/{safe_user_id}/drive",
            params={"$select": "id,webUrl,driveType"},
            max_attempts=8,
        )
        data = response.json()
        return {"id": data.get("id"), "webUrl": data.get("webUrl"), "driveType": data.get("driveType")}

    def get_drive(self, drive_id=None):
        """Get drive."""
        drive_id = drive_id or self.drive_id
        url = f"/drives/{drive_id}"
        response = self.get(url)
        return response.json()

    def get_drive_root(self):
        """Get drive root."""
        url = f"/drives/{self.drive_id}/root"
        response = self.get(url)
        return response.json()

    def list_drive_items(self, folder_id=None):
        """List drive items."""
        if folder_id:
            url = f"/drives/{self.drive_id}/items/{folder_id}/children"
        else:
            url = f"/drives/{self.drive_id}/root/children"

        response = self.get(url)
        return response.json().get("value", [])

    def download_file(self, item_id, destination_path):
        """Run download file."""
        url = f"/drives/{self.drive_id}/items/{item_id}/content"
        response = self.get(url, stream=True)

        with open(destination_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"File downloaded to {destination_path}")

    def upload_file(self, source_path, parent_folder_id=None):
        """Run upload file."""
        file_name = Path(source_path).name
        if parent_folder_id:
            url = f"/drives/{self.drive_id}/items/{parent_folder_id}:/{file_name}:/content"
        else:
            url = f"/drives/{self.drive_id}/root:/{file_name}:/content"

        with open(source_path, "rb") as file:
            response = self.put(url, data=file)

        print(f"File uploaded: {response.json().get('id')}")
        return response.json()

    def create_upload_session(self, item_path, parent_folder_id=None, conflict_behavior="replace"):
        """Create upload session."""
        if parent_folder_id:
            url = f"/drives/{self.drive_id}/items/{parent_folder_id}:/{item_path}:/createUploadSession"
        else:
            url = f"/drives/{self.drive_id}/root:/{item_path}:/createUploadSession"
        payload = {"item": {"@microsoft.graph.conflictBehavior": conflict_behavior}}
        response = self.post(url, json=payload)
        return response.json()

    def create_folder(self, folder_name, parent_folder_id=None):
        """Create folder."""
        if parent_folder_id:
            url = f"/drives/{self.drive_id}/items/{parent_folder_id}/children"
        else:
            url = f"/drives/{self.drive_id}/root/children"

        folder_data = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename",
        }

        response = self.post(url, json=folder_data)
        print(f"Folder created: {response.json().get('id')}")
        return response.json()

    def get_item_by_path(self, item_path):
        """Get item by path."""
        url = f"/drives/{self.drive_id}/root:/{item_path}"
        response = self.get(url)
        return response.json()

    def update_item(self, item_id, updates):
        """Update item."""
        url = f"/drives/{self.drive_id}/items/{item_id}"
        response = self.patch(url, json=updates)
        return response.json()

    def move_item(self, item_id, new_parent_id, new_name=None):
        """Run move item."""
        url = f"/drives/{self.drive_id}/items/{item_id}"
        payload = {"parentReference": {"id": new_parent_id}}
        if new_name:
            payload["name"] = new_name
        response = self.patch(url, json=payload)
        return response.json()

    def copy_item(self, item_id, new_parent_id, new_name=None):
        """Run copy item."""
        url = f"/drives/{self.drive_id}/items/{item_id}/copy"
        payload = {"parentReference": {"id": new_parent_id}}
        if new_name:
            payload["name"] = new_name
        response = self.post(url, json=payload)
        return response.json()

    def delete_item(self, item_id):
        """Delete item."""
        url = f"/drives/{self.drive_id}/items/{item_id}"
        self.delete(url)
        print(f"Item {item_id} deleted.")

    def get_item_metadata(self, item_id):
        """Get item metadata."""
        url = f"/drives/{self.drive_id}/items/{item_id}"
        response = self.get(url)
        return response.json()

    def list_item_permissions(self, item_id):
        """List item permissions."""
        url = f"/drives/{self.drive_id}/items/{item_id}/permissions"
        response = self.get(url)
        return response.json().get("value", [])

    def delete_permission(self, item_id, permission_id):
        """Delete permission."""
        url = f"/drives/{self.drive_id}/items/{item_id}/permissions/{permission_id}"
        self.delete(url)
        return True

    def search_items(self, query):
        """Run search items."""
        url = f"/drives/{self.drive_id}/root/search(q='{query}')"
        response = self.get(url)
        return response.json().get("value", [])

    def share_item(self, item_id, recipients, message="", require_sign_in=True, send_invitation=True):
        """Run share item."""
        url = f"/drives/{self.drive_id}/items/{item_id}/createLink"
        share_data = {"type": "view", "scope": "organization"}

        response = self.post(url, json=share_data)
        link = response.json().get("link", {}).get("webUrl")

        invitation_url = f"/drives/{self.drive_id}/items/{item_id}/invite"
        invite_data = {
            "recipients": [{"email": r} for r in recipients],
            "message": message,
            "requireSignIn": require_sign_in,
            "sendInvitation": send_invitation,
            "roles": ["read"],
        }

        self.post(invitation_url, json=invite_data)
        print(f"Item shared. Link: {link}")
        return link

    def get_drive_usage(self):
        """Get drive usage."""
        url = f"/drives/{self.drive_id}"
        response = self.get(url)
        drive_info = response.json()
        usage = drive_info.get("quota", {})
        return usage

    def get_recent_items(self, days=7):
        """Get recent items."""
        url = f"/drives/{self.drive_id}/root/delta"
        recent_items = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        while url:
            response = self.get(url)
            data = response.json()
            for item in data.get("value", []):
                last_modified_str = item.get("lastModifiedDateTime")
                if last_modified_str:
                    last_modified = datetime.fromisoformat(last_modified_str.replace("Z", "+00:00"))
                    if last_modified >= cutoff_date:
                        recent_items.append(item)
            url = data.get("@odata.nextLink")

        return recent_items

    def mirror_to_local(self, source_folder_id, destination_folder_path):
        """Run mirror to local."""
        items = self.list_drive_items(folder_id=source_folder_id)
        for item in items:
            item_id = item["id"]
            item_name = item["name"]
            if "folder" in item:
                new_dest_folder = Path(destination_folder_path) / item_name
                new_dest_folder.mkdir(parents=True, exist_ok=True)
                self.mirror_to_local(item_id, new_dest_folder)
            else:
                dest_path = Path(destination_folder_path) / item_name
                self.download_file(item_id, dest_path)

    def mirror_from_local(self, source_folder_path, destination_folder_id):
        """Run mirror from local."""
        for item in Path(source_folder_path).iterdir():
            if item.is_dir():
                new_dest_folder = self.create_folder(item.name, parent_folder_id=destination_folder_id)
                self.mirror_from_local(item, new_dest_folder["id"])
            else:
                self.upload_file(item, parent_folder_id=destination_folder_id)

    def list_personal_sites_powershell(self, limit="All", filter_query=None, **powershell_options):
        """List personal sites powershell."""
        params = {"IncludePersonalSite": True, "Limit": limit}
        if filter_query:
            params["Filter"] = filter_query
        cmd = "Get-SPOSite" + _ps_params(params)
        return self._get_powershell(**powershell_options).run_json(cmd)

    def get_personal_site_powershell(self, site_url, **powershell_options):
        """Get personal site powershell."""
        cmd = "Get-SPOSite" + _ps_params({"Identity": site_url})
        return self._get_powershell(**powershell_options).run_json(cmd)

    def set_personal_site_powershell(self, site_url, **properties):
        """Set personal site powershell."""
        params = {"Identity": site_url}
        params.update(properties)
        cmd = "Set-SPOSite" + _ps_params(params)
        return self._get_powershell().run(cmd)

    def remove_personal_site_powershell(self, site_url, **powershell_options):
        """Remove personal site powershell."""
        cmd = "Remove-SPOSite" + _ps_params({"Identity": site_url, "Confirm": False})
        return self._get_powershell(**powershell_options).run(cmd)

    def restore_personal_site_powershell(self, site_url, **powershell_options):
        """Run restore personal site powershell."""
        cmd = "Restore-SPODeletedSite" + _ps_params({"Identity": site_url})
        return self._get_powershell(**powershell_options).run(cmd)

    def set_personal_site_quota_powershell(self, site_url, storage_quota=None, warning_quota=None, **powershell_options):
        """Set personal site quota powershell."""
        params = {
            "Identity": site_url,
            "StorageQuota": storage_quota,
            "StorageQuotaWarningLevel": warning_quota,
        }
        cmd = "Set-SPOSite" + _ps_params(params)
        return self._get_powershell(**powershell_options).run(cmd)


class OneDrivePowerShellClient(PowerShellModuleClient):
    """Client for One Drive Power Shell operations."""
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
