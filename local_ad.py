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


class LocalADClient:
    def __init__(self, powershell=None, powershell_options=None):
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = LocalADPowerShellClient(**options)
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

    def list_users(self, name=None):
        cmd = "Get-ADUser" + _ps_params({"Filter": f"Name -like '{_ps_quote(name)}'" if name else "*"})
        return self._get_powershell().run_json(cmd)

    def create_user(self, name, sam_account_name, user_principal_name, password, ou_dn=None, enabled=True):
        secure = f"(ConvertTo-SecureString '{_ps_quote(password)}' -AsPlainText -Force)"
        params = {
            "Name": name,
            "SamAccountName": sam_account_name,
            "UserPrincipalName": user_principal_name,
            "AccountPassword": secure,
            "Enabled": enabled,
            "Path": ou_dn,
        }
        cmd = "New-ADUser" + _ps_params(params)
        return self._get_powershell().run(cmd)

    def reset_password(self, user_dn, password, unlock=False):
        secure = f"(ConvertTo-SecureString '{_ps_quote(password)}' -AsPlainText -Force)"
        cmd = "Set-ADAccountPassword" + _ps_params({"Identity": user_dn, "Reset": True, "NewPassword": secure})
        script = cmd
        if unlock:
            script += f"; Unlock-ADAccount -Identity '{_ps_quote(user_dn)}'"
        return self._get_powershell().run(script)

    def unlock_account(self, user_dn):
        cmd = "Unlock-ADAccount" + _ps_params({"Identity": user_dn})
        return self._get_powershell().run(cmd)

    def enable_account(self, user_dn):
        cmd = "Enable-ADAccount" + _ps_params({"Identity": user_dn})
        return self._get_powershell().run(cmd)

    def disable_account(self, user_dn):
        cmd = "Disable-ADAccount" + _ps_params({"Identity": user_dn})
        return self._get_powershell().run(cmd)

    def list_groups(self, name=None):
        cmd = "Get-ADGroup" + _ps_params({"Filter": f"Name -like '{_ps_quote(name)}'" if name else "*"})
        return self._get_powershell().run_json(cmd)

    def create_group(self, name, sam_account_name=None, ou_dn=None, scope="Global", category="Security"):
        params = {
            "Name": name,
            "SamAccountName": sam_account_name,
            "Path": ou_dn,
            "GroupScope": scope,
            "GroupCategory": category,
        }
        cmd = "New-ADGroup" + _ps_params(params)
        return self._get_powershell().run(cmd)

    def add_group_member(self, group_dn, member_dn):
        cmd = "Add-ADGroupMember" + _ps_params({"Identity": group_dn, "Members": [member_dn]})
        return self._get_powershell().run(cmd)

    def remove_group_member(self, group_dn, member_dn):
        cmd = "Remove-ADGroupMember" + _ps_params({"Identity": group_dn, "Members": [member_dn], "Confirm": False})
        return self._get_powershell().run(cmd)

    def move_user_to_ou(self, user_dn, ou_dn):
        cmd = "Move-ADObject" + _ps_params({"Identity": user_dn, "TargetPath": ou_dn})
        return self._get_powershell().run(cmd)

    def list_ous(self, name=None):
        cmd = "Get-ADOrganizationalUnit" + _ps_params({"Filter": f"Name -like '{_ps_quote(name)}'" if name else "*"})
        return self._get_powershell().run_json(cmd)

    def list_gpos(self, name=None):
        cmd = "Get-GPO" + _ps_params({"Name": name} if name else {"All": True})
        return self._get_powershell().run_json(cmd)

    def get_gpo_inheritance(self, ou_dn):
        cmd = "Get-GPInheritance" + _ps_params({"Target": ou_dn})
        return self._get_powershell().run_json(cmd)

    def link_gpo(self, gpo_name, ou_dn, enforced=False):
        cmd = "New-GPLink" + _ps_params({"Name": gpo_name, "Target": ou_dn, "Enforced": enforced})
        return self._get_powershell().run(cmd)

    def unlink_gpo(self, gpo_name, ou_dn):
        cmd = "Remove-GPLink" + _ps_params({"Name": gpo_name, "Target": ou_dn, "Confirm": False})
        return self._get_powershell().run(cmd)

    def backup_gpo(self, gpo_name, path, comment=None):
        params = {"Name": gpo_name, "Path": path, "Comment": comment}
        cmd = "Backup-GPO" + _ps_params(params)
        return self._get_powershell().run_json(cmd)

    def restore_gpo(self, gpo_name, path):
        cmd = "Restore-GPO" + _ps_params({"Name": gpo_name, "Path": path})
        return self._get_powershell().run(cmd)


class LocalADPowerShellClient(PowerShellModuleClient):
    def __init__(self, session=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        if self.connect_script:
            return self.connect_script
        return "Import-Module ActiveDirectory; Import-Module GroupPolicy"

    def _disconnect_script(self):
        return self.disconnect_script
