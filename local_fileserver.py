from microsoft import PowerShellModuleClient, is_powershell_envelope, unwrap_powershell_data


class LocalFileServerClient:
    """Client for Local File Server operations."""
    def __init__(self, powershell=None, powershell_options=None):
        """Initialize the instance."""
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        """Get powershell."""
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = LocalFileServerPowerShellClient(**options)
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
        """List files."""
        if not unc_path:
            raise ValueError("UNC path is required, e.g. \\\\server\\share")
        if (username and not password) or (password and not username):
            raise ValueError("Both username and password are required when using explicit credentials.")

        params = {
            "unc_path": unc_path,
            "username": username,
            "password": password,
            "recurse": bool(recurse),
            "include_directories": bool(include_directories),
            "include_hidden": bool(include_hidden),
            "max_items": int(max_items) if max_items else None,
        }

        script = """
        $root = $unc_path
        $username = $username
        $password = $password
        $recurse = [bool]$recurse
        $includeDirs = [bool]$include_directories
        $includeHidden = [bool]$include_hidden
        $maxItems = $max_items
        $drive = 'FS' + ([guid]::NewGuid().ToString('N').Substring(0, 6))

        $cred = $null
        if ($username -and $password) {
          $secure = ConvertTo-SecureString $password -AsPlainText -Force
          $cred = New-Object System.Management.Automation.PSCredential($username, $secure)
        }

        try {
          if ($cred) {
            New-PSDrive -Name $drive -PSProvider FileSystem -Root $root -Credential $cred -ErrorAction Stop | Out-Null
          } else {
            New-PSDrive -Name $drive -PSProvider FileSystem -Root $root -ErrorAction Stop | Out-Null
          }

          $path = \"$drive:\\\"
          $flags = @()
          if ($recurse) { $flags += '-Recurse' }
          if ($includeHidden) { $flags += '-Force' }
          if (-not $includeDirs) { $flags += '-File' }

          $items = Get-ChildItem -LiteralPath $path @flags -ErrorAction SilentlyContinue
          $total = @($items).Count
          if ($maxItems) {
            $items = $items | Select-Object -First $maxItems
          }

          $rows = foreach ($item in $items) {
            $fullPath = $item.FullName
            if ($fullPath -like \"$drive:*\") {
              $fullPath = $fullPath -replace ([regex]::Escape($drive + ':\\')), ($root + '\\')
            }
            $isHidden = $false
            if ($item.Attributes) {
              $isHidden = (($item.Attributes -band [IO.FileAttributes]::Hidden) -ne 0)
            }
            [PSCustomObject]@{
              path = $fullPath
              name = $item.Name
              type = if ($item.PSIsContainer) { 'directory' } else { 'file' }
              size = if ($item.PSIsContainer) { $null } else { $item.Length }
              modified = $item.LastWriteTimeUtc
              hidden = $isHidden
            }
          }

          [PSCustomObject]@{
            rows = $rows
            total_count = $total
            returned_count = @($rows).Count
          }
        } finally {
          Remove-PSDrive -Name $drive -ErrorAction SilentlyContinue | Out-Null
        }
        """

        result = self._get_powershell().run_json(script, parameters=params)
        if is_powershell_envelope(result):
            if not result.get("ok", True):
                return result
            payload = unwrap_powershell_data(result) or {}
            rows = payload.get("rows") or []
            meta = dict(result.get("meta") or {})
            meta["summary"] = {
                "total_count": payload.get("total_count"),
                "returned_count": payload.get("returned_count"),
            }
            return {**result, "data": rows, "meta": meta}
        return result


class LocalFileServerPowerShellClient(PowerShellModuleClient):
    """Client for Local File Server Power Shell operations."""
    def __init__(self, session=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        """Initialize the instance."""
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        """Internal helper for connect script."""
        return self.connect_script

    def _disconnect_script(self):
        """Internal helper for disconnect script."""
        return self.disconnect_script
