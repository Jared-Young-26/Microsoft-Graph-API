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


class LocalRegistryClient:
    def __init__(self, powershell=None, powershell_options=None):
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = LocalRegistryPowerShellClient(**options)
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

    def watchlist_snapshot(self, paths=None, recurse_depth=0, max_items=200):
        script = r"""
param($paths, $depth, $maxItems)

$results = New-Object System.Collections.ArrayList

function Get-ValueHash($value) {
  try {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes([string]$value)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $hash = $sha.ComputeHash($bytes)
    return ([System.BitConverter]::ToString($hash)).Replace('-', '').ToLower()
  } catch {
    return $null
  }
}

function Normalize-Value($name, $value) {
  if ($null -eq $value) { return $null }
  if ($value -is [byte[]]) {
    return "sha256:" + (Get-ValueHash ([System.Convert]::ToBase64String($value)))
  }
  if ($value -is [string]) {
    $lower = $name.ToLower()
    if ($lower -match "password|secret|token|key|credential") {
      return "[redacted]"
    }
    if ($value.Length -gt 120) {
      return "sha256:" + (Get-ValueHash $value)
    }
    return $value
  }
  if ($value -is [int] -or $value -is [long] -or $value -is [double]) {
    return $value
  }
  return "sha256:" + (Get-ValueHash ($value | Out-String))
}

function Add-Entry($path) {
  if ($results.Count -ge $maxItems) { return }
  if (-not (Test-Path $path)) { return }
  try {
    $item = Get-Item -Path $path -ErrorAction Stop
    $props = Get-ItemProperty -Path $path -ErrorAction Stop
    $values = @{}
    $types = @{}
    foreach ($prop in $props.PSObject.Properties) {
      if ($prop.Name -in "PSPath","PSParentPath","PSChildName","PSDrive","PSProvider") { continue }
      $values[$prop.Name] = (Normalize-Value $prop.Name $prop.Value)
      $types[$prop.Name] = $prop.TypeNameOfValue
    }
    $entry = [PSCustomObject]@{
      path = $path
      values = $values
      value_types = $types
      last_write_time = $item.LastWriteTime
    }
    [void]$results.Add($entry)
  } catch {
    $entry = [PSCustomObject]@{
      path = $path
      error = $_.Exception.Message
    }
    [void]$results.Add($entry)
  }
}

function Walk-Registry($path, $depth) {
  Add-Entry $path
  if ($depth -le 0 -or $results.Count -ge $maxItems) { return }
  try {
    $children = Get-ChildItem -Path $path -ErrorAction SilentlyContinue
    foreach ($child in $children) {
      if ($results.Count -ge $maxItems) { return }
      Walk-Registry $child.PSPath ($depth - 1)
    }
  } catch {
    return
  }
}

foreach ($path in ($paths | Where-Object { $_ -ne $null -and $_ -ne "" })) {
  Walk-Registry $path $depth
}

[PSCustomObject]@{
  count = $results.Count
  items = $results
}
"""
        return self._get_powershell().run_json(
            script,
            parameters={
                "paths": paths or [],
                "depth": int(recurse_depth) if recurse_depth is not None else 0,
                "maxItems": int(max_items) if max_items else 200,
            },
            depth=6,
        )

    def export_reg(self, path, output_path=None):
        if not path:
            raise ValueError("Registry path is required.")
        script = f"""
        $path = '{_ps_quote(path)}'
        $dest = {_ps_value(output_path)}
        if (-not $dest) {{
          $dest = Join-Path $env:TEMP ("reg_export_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".reg")
        }}
        reg export "$path" "$dest" /y | Out-String | Out-Null
        [PSCustomObject]@{{ export_path = $dest; registry_path = $path }}
        """
        return self._get_powershell().run_json(script, depth=4)

    def save_hive(self, hive, output_path=None):
        if not hive:
            raise ValueError("Hive is required (e.g., HKLM\\SYSTEM).")
        script = f"""
        $hive = '{_ps_quote(hive)}'
        $dest = {_ps_value(output_path)}
        if (-not $dest) {{
          $dest = Join-Path $env:TEMP ("hive_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".hiv")
        }}
        reg save "$hive" "$dest" /y | Out-String | Out-Null
        [PSCustomObject]@{{ hive = $hive; hive_path = $dest }}
        """
        return self._get_powershell().run_json(script, depth=4)


class LocalRegistryPowerShellClient(PowerShellModuleClient):
    def __init__(self, session=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        return self.connect_script

    def _disconnect_script(self):
        return self.disconnect_script
