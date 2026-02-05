from microsoft import PowerShellModuleClient, is_powershell_envelope, unwrap_powershell_data


def _parse_gpresult_summary(text):
    """Parse gpresult summary."""
    summary = {"user": {}, "computer": {}, "applied_gpos": {"user": [], "computer": []}}
    section = None
    collecting = False
    for line in str(text or "").splitlines():
        stripped = line.strip()
        if not stripped:
            if collecting:
                collecting = False
            continue
        lower = stripped.lower()
        if lower.startswith("computer settings"):
            section = "computer"
            collecting = False
            continue
        if lower.startswith("user settings"):
            section = "user"
            collecting = False
            continue
        if "applied group policy objects" in lower:
            collecting = True
            continue
        if collecting and section:
            if lower.startswith("the following gpos were not applied"):
                collecting = False
                continue
            summary["applied_gpos"][section].append(stripped)
            continue
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            mapped = None
            if key.lower().startswith("domain name"):
                mapped = "domain"
            elif key.lower().startswith("computer name"):
                mapped = "computer_name"
            elif key.lower().startswith("user name"):
                mapped = "user_name"
            elif key.lower().startswith("last time group policy was applied"):
                mapped = "last_applied"
            elif key.lower().startswith("group policy was applied from"):
                mapped = "applied_from"
            if mapped and section:
                summary[section][mapped] = value
    return summary


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


def _wrap_envelope(result, payload_builder):
    """Internal helper for wrap envelope."""
    if is_powershell_envelope(result):
        if not result.get("ok", True):
            return result
        data = unwrap_powershell_data(result)
        payload = payload_builder(data)
        return {**result, "data": payload}
    return payload_builder(result)


class LocalADClient:
    """Client for Local A D operations."""
    def __init__(self, powershell=None, powershell_options=None):
        """Initialize the instance."""
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        """Get powershell."""
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = LocalADPowerShellClient(**options)
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

    def list_users(self, name=None):
        """List users."""
        cmd = "Get-ADUser" + _ps_params({"Filter": f"Name -like '{_ps_quote(name)}'" if name else "*"})
        return self._get_powershell().run_json(cmd)

    def create_user(self, name, sam_account_name, user_principal_name, password, ou_dn=None, enabled=True):
        """Create user."""
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
        """Run reset password."""
        secure = f"(ConvertTo-SecureString '{_ps_quote(password)}' -AsPlainText -Force)"
        cmd = "Set-ADAccountPassword" + _ps_params({"Identity": user_dn, "Reset": True, "NewPassword": secure})
        script = cmd
        if unlock:
            script += f"; Unlock-ADAccount -Identity '{_ps_quote(user_dn)}'"
        return self._get_powershell().run(script)

    def unlock_account(self, user_dn):
        """Run unlock account."""
        cmd = "Unlock-ADAccount" + _ps_params({"Identity": user_dn})
        return self._get_powershell().run(cmd)

    def enable_account(self, user_dn):
        """Run enable account."""
        cmd = "Enable-ADAccount" + _ps_params({"Identity": user_dn})
        return self._get_powershell().run(cmd)

    def disable_account(self, user_dn):
        """Run disable account."""
        cmd = "Disable-ADAccount" + _ps_params({"Identity": user_dn})
        return self._get_powershell().run(cmd)

    def list_groups(self, name=None):
        """List groups."""
        cmd = "Get-ADGroup" + _ps_params({"Filter": f"Name -like '{_ps_quote(name)}'" if name else "*"})
        return self._get_powershell().run_json(cmd)

    def create_group(self, name, sam_account_name=None, ou_dn=None, scope="Global", category="Security"):
        """Create group."""
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
        """Add group member."""
        cmd = "Add-ADGroupMember" + _ps_params({"Identity": group_dn, "Members": [member_dn]})
        return self._get_powershell().run(cmd)

    def remove_group_member(self, group_dn, member_dn):
        """Remove group member."""
        cmd = "Remove-ADGroupMember" + _ps_params({"Identity": group_dn, "Members": [member_dn], "Confirm": False})
        return self._get_powershell().run(cmd)

    def move_user_to_ou(self, user_dn, ou_dn):
        """Run move user to ou."""
        cmd = "Move-ADObject" + _ps_params({"Identity": user_dn, "TargetPath": ou_dn})
        return self._get_powershell().run(cmd)

    def list_ous(self, name=None):
        """List ous."""
        cmd = "Get-ADOrganizationalUnit" + _ps_params({"Filter": f"Name -like '{_ps_quote(name)}'" if name else "*"})
        return self._get_powershell().run_json(cmd)

    def list_gpos(self, name=None):
        """List gpos."""
        cmd = "Get-GPO" + _ps_params({"Name": name} if name else {"All": True})
        return self._get_powershell().run_json(cmd)

    def get_gpo_inheritance(self, ou_dn):
        """Get gpo inheritance."""
        cmd = "Get-GPInheritance" + _ps_params({"Target": ou_dn})
        return self._get_powershell().run_json(cmd)

    def get_gpo_links(self, ou_dn):
        """Get gpo links."""
        script = f"""
        $target = {_ps_value(ou_dn)}
        $inherit = Get-GPInheritance -Target $target
        $direct = @()
        $inherited = @()
        if ($inherit.GpoLinks) {{
          $direct = $inherit.GpoLinks | Select-Object DisplayName,Enabled,Enforced,Order,GpoId,Target
        }}
        if ($inherit.InheritedGpoLinks) {{
          $inherited = $inherit.InheritedGpoLinks | Select-Object DisplayName,Enabled,Enforced,Order,GpoId,Target
        }}
        [PSCustomObject]@{{
          target = $target
          gpo_links = $direct
          inherited_links = $inherited
          block_inheritance = $inherit.BlockInheritance
        }}
        """
        return self._get_powershell().run_json(script)

    def get_gpo_report(self, name, report_type="Xml", output_path=None):
        """Get gpo report."""
        if not name:
            raise ValueError("GPO name is required.")
        report_type = report_type or "Xml"
        script = f"""
        $name = {_ps_value(name)}
        $type = '{_ps_quote(report_type)}'
        $path = {_ps_value(output_path)}
        if (-not $path) {{
          $ext = if ($type -match 'html') {{ 'html' }} else {{ 'xml' }}
          $path = Join-Path $env:TEMP ("gpo_report_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".$ext")
        }}
        Get-GPOReport -Name $name -ReportType $type -Path $path
        [PSCustomObject]@{{
          name = $name
          report_type = $type
          report_path = $path
        }}
        """
        return self._get_powershell().run_json(script)

    def get_gppref_registry_value(self, gpo_name, key, value_name=None):
        """Get gppref registry value."""
        if not gpo_name or not key:
            raise ValueError("GPO name and registry key are required.")
        params = {"Name": gpo_name, "Key": key}
        if value_name:
            params["ValueName"] = value_name
        cmd = "Get-GPPrefRegistryValue" + _ps_params(params)
        return self._get_powershell().run_json(cmd)

    def link_gpo(self, gpo_name, ou_dn, enforced=False):
        """Run link gpo."""
        cmd = "New-GPLink" + _ps_params({"Name": gpo_name, "Target": ou_dn, "Enforced": enforced})
        return self._get_powershell().run(cmd)

    def unlink_gpo(self, gpo_name, ou_dn):
        """Run unlink gpo."""
        cmd = "Remove-GPLink" + _ps_params({"Name": gpo_name, "Target": ou_dn, "Confirm": False})
        return self._get_powershell().run(cmd)

    def backup_gpo(self, gpo_name, path, comment=None):
        """Run backup gpo."""
        params = {"Name": gpo_name, "Path": path, "Comment": comment}
        cmd = "Backup-GPO" + _ps_params(params)
        return self._get_powershell().run_json(cmd)

    def restore_gpo(self, gpo_name, path):
        """Run restore gpo."""
        cmd = "Restore-GPO" + _ps_params({"Name": gpo_name, "Path": path})
        return self._get_powershell().run(cmd)

    def gpresult_report(self, report_type="summary", output_path=None, include_summary=False):
        """Run gpresult report."""
        report_type = (report_type or "summary").lower()
        if report_type in {"html", "h"}:
            script = f"""
            $path = {_ps_value(output_path)}
            if (-not $path) {{
              $path = Join-Path $env:TEMP ("gpresult_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".html")
            }}
            gpresult /h $path /f | Out-String | Out-Null
            [PSCustomObject]@{{ report_path = $path; report_type = 'html' }}
            """
            result = self._get_powershell().run_json(script)
            if include_summary and is_powershell_envelope(result) and result.get("ok", True):
                summary_result = self._get_powershell().run("gpresult /r")
                if is_powershell_envelope(summary_result) and summary_result.get("ok", True):
                    raw = unwrap_powershell_data(summary_result)
                    summary = _parse_gpresult_summary(raw)
                    payload = unwrap_powershell_data(result) or {}
                    payload["summary"] = summary
                    return {**result, "data": payload}
            return result
        result = self._get_powershell().run("gpresult /r")
        wrapped = _wrap_envelope(result, lambda output: {"raw_text": output, "report_type": "summary"})
        if include_summary and is_powershell_envelope(wrapped) and wrapped.get("ok", True):
            raw = unwrap_powershell_data(wrapped).get("raw_text")
            summary = _parse_gpresult_summary(raw)
            payload = unwrap_powershell_data(wrapped) or {}
            payload["summary"] = summary
            return {**wrapped, "data": payload}
        return wrapped


class LocalADPowerShellClient(PowerShellModuleClient):
    """Client for Local A D Power Shell operations."""
    def __init__(self, session=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        """Initialize the instance."""
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        """Internal helper for connect script."""
        if self.connect_script:
            return self.connect_script
        return "Import-Module ActiveDirectory; Import-Module GroupPolicy"

    def _disconnect_script(self):
        """Internal helper for disconnect script."""
        return self.disconnect_script
