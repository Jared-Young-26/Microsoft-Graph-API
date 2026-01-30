import uuid

from microsoft import PowerShellModuleClient


def _ps_quote(value):
    return str(value).replace("'", "''")


class LocalFileServerClient:
    def __init__(self, powershell=None, powershell_options=None):
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = LocalFileServerPowerShellClient(**options)
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

    def list_files(
        self,
        unc_path,
        username=None,
        password=None,
        recurse=True,
        include_directories=False,
        include_hidden=False,
        max_items=None,
    ):
        if not unc_path:
            raise ValueError("UNC path is required, e.g. \\\\server\\share")
        if (username and not password) or (password and not username):
            raise ValueError("Both username and password are required when using explicit credentials.")

        drive_name = f"FS{uuid.uuid4().hex[:6]}"
        flags = []
        if recurse:
            flags.append("-Recurse")
        if include_hidden:
            flags.append("-Force")
        if not include_directories:
            flags.append("-File")
        flags_str = " ".join(flags)
        limit = f"| Select-Object -First {int(max_items)}" if max_items else ""

        cred_script = "$cred = $null"
        if username and password:
            cred_script = (
                f"$secure = ConvertTo-SecureString '{_ps_quote(password)}' -AsPlainText -Force\n"
                f"$cred = New-Object System.Management.Automation.PSCredential('{_ps_quote(username)}', $secure)"
            )

        script = f"""
        {cred_script}
        $drive = '{drive_name}'
        $root = '{_ps_quote(unc_path)}'
        if ($cred) {{
          New-PSDrive -Name $drive -PSProvider FileSystem -Root $root -Credential $cred -ErrorAction Stop | Out-Null
        }} else {{
          New-PSDrive -Name $drive -PSProvider FileSystem -Root $root -ErrorAction Stop | Out-Null
        }}
        $path = "$drive:\\"
        $items = Get-ChildItem -LiteralPath $path {flags_str} -ErrorAction SilentlyContinue {limit}
        $items | Select-Object FullName, Name, Extension, Length, Directory, LastWriteTimeUtc
        Remove-PSDrive -Name $drive -ErrorAction SilentlyContinue
        """
        return self._get_powershell().run_json(script)


class LocalFileServerPowerShellClient(PowerShellModuleClient):
    def __init__(self, session=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        return self.connect_script

    def _disconnect_script(self):
        return self.disconnect_script
