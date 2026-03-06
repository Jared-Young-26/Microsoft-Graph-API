from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import os
import platform
import re
import secrets
import zipfile

from ..powershell import PowerShellRunner
from ..token_store import AgentTokenStore
from .interface import ActionDefinition, ActionResult
from .manifest import load_manifest_for_plugin


def _is_windows() -> bool:
    return platform.system().lower() == "windows"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_bool(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes", "y", "on")


def _as_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _as_int(value: Any, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except Exception:
        return default


def _tail_bytes(path: Path, max_bytes: int) -> bytes:
    try:
        size = path.stat().st_size
    except Exception:
        return b""
    try:
        with path.open("rb") as handle:
            if size > max_bytes:
                handle.seek(size - max_bytes)
            return handle.read()
    except Exception:
        return b""


def _is_safe_module_name(name: str) -> bool:
    if not name:
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", name))


DEFAULT_REQUIRED_MODULES = [
    "Microsoft.Graph",
    "Az.Accounts",
    "MicrosoftTeams",
    "ExchangeOnlineManagement",
    "Microsoft.Online.SharePoint.PowerShell",
]


@dataclass
class WindowsPowerShellRunnerPlugin:
    """Windows PowerShell runner plugin (queries + health)."""

    id: str = "windows_powershell_runner"

    def capabilities(self) -> list[str]:
        caps = ["evidence.bundle_zip"]
        if _is_windows() and self._runner().is_available():
            caps.extend(
                [
                    "powershell.core",
                    "query.eventlog",
                    "query.registry",
                    "query.files",
                    "query.processes",
                    "query.network_probe",
                ]
            )
        return caps

    def actions(self) -> list[ActionDefinition]:
        manifest_actions = load_manifest_for_plugin(self.id)
        if manifest_actions:
            return manifest_actions
        return [
            ActionDefinition(
                action_id="powershell.whoami_all",
                title="whoami /all",
                description="Return current identity, groups, and token characteristics (structured).",
                required_capabilities=["powershell.core"],
                risk_level="safe",
            ),
            ActionDefinition(
                action_id="powershell.module_inventory",
                title="Module inventory",
                description="List installed PowerShell modules and versions.",
                required_capabilities=["powershell.core"],
                risk_level="safe",
            ),
            ActionDefinition(
                action_id="powershell.health_check",
                title="PowerShell health check",
                description="Check pwsh version, required modules, admin rights, domain join, and DC connectivity.",
                required_capabilities=["powershell.core"],
                risk_level="caution",
            ),
            ActionDefinition(
                action_id="query.eventlog",
                title="Query event logs",
                description="Read-only event log query via Get-WinEvent.",
                required_capabilities=["powershell.core", "query.eventlog"],
                risk_level="safe",
            ),
            ActionDefinition(
                action_id="query.registry",
                title="Query registry",
                description="Read-only registry query.",
                required_capabilities=["powershell.core", "query.registry"],
                risk_level="safe",
            ),
            ActionDefinition(
                action_id="query.files",
                title="Query files",
                description="Read-only file enumeration restricted to allowed roots.",
                required_capabilities=["powershell.core", "query.files"],
                risk_level="safe",
            ),
            ActionDefinition(
                action_id="query.processes",
                title="Query processes",
                description="Process list with optional command line.",
                required_capabilities=["powershell.core", "query.processes"],
                risk_level="safe",
            ),
            ActionDefinition(
                action_id="query.network_probe",
                title="Network probe",
                description="DNS/TCP/ping/traceroute probes.",
                required_capabilities=["powershell.core", "query.network_probe"],
                risk_level="safe",
            ),
            ActionDefinition(
                action_id="evidence.bundle_zip",
                title="Evidence bundle (zip)",
                description="Bundle agent logs + last job results + selected artifacts into a zip for upload.",
                required_capabilities=["evidence.bundle_zip"],
                risk_level="safe",
            ),
        ]

    def _runner(self) -> PowerShellRunner:
        return PowerShellRunner()

    def _allow_module_install(self) -> bool:
        return _parse_bool(os.environ.get("ALLOW_MODULE_INSTALL"))

    def _unsupported(self) -> ActionResult:
        return ActionResult(ok=False, stderr="Unsupported platform: Windows required.", exit_code=2)

    def handle(self, action_id: str, params: dict | None) -> ActionResult:
        params = params or {}
        if action_id == "evidence.bundle_zip":
            return self._evidence_bundle(params)
        if not _is_windows():
            return self._unsupported()

        if action_id == "powershell.whoami_all":
            return self._whoami_all()
        if action_id == "powershell.module_inventory":
            return self._module_inventory()
        if action_id == "powershell.health_check":
            return self._health_check(params)
        if action_id == "query.eventlog":
            return self._query_eventlog(params)
        if action_id == "query.registry":
            return self._query_registry(params)
        if action_id == "query.files":
            return self._query_files(params)
        if action_id == "query.processes":
            return self._query_processes(params)
        if action_id == "query.network_probe":
            return self._query_network_probe(params)
        return ActionResult(ok=False, stderr=f"Unknown action_id: {action_id}", exit_code=2)

    def _ps(self, script_body: str, params: dict[str, Any] | None = None, timeout_seconds: int | None = None) -> ActionResult:
        runner = self._runner()
        result = runner.run_json(script_body, params=params, timeout_seconds=timeout_seconds)
        if not result.ok:
            return ActionResult(ok=False, result=result.data, stdout=result.stdout, stderr=result.error or result.stderr, exit_code=1)
        return ActionResult(ok=True, result=result.data, stdout=result.stdout, stderr=result.stderr, exit_code=0)

    def _whoami_all(self) -> ActionResult:
        script = r"""
$id = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object System.Security.Principal.WindowsPrincipal($id)
$groups = @()
foreach ($sid in ($id.Groups | Where-Object { $_ })) {
  $name = $null
  try { $name = $sid.Translate([System.Security.Principal.NTAccount]).Value } catch { $name = $null }
  $groups += [pscustomobject]@{
    sid = $sid.Value
    name = $name
  }
}
$whoami = $null
try { $whoami = (& whoami /all 2>&1 | Out-String).Trim() } catch { $whoami = $null }
$out = [pscustomobject]@{
  identity = [pscustomobject]@{
    name = $id.Name
    sid = $id.User.Value
    authentication_type = $id.AuthenticationType
    is_authenticated = $id.IsAuthenticated
    is_system = $id.IsSystem
    is_admin = $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
    groups = $groups
  }
  whoami_all = $whoami
}
"""
        return self._ps(script, timeout_seconds=30)

    def _module_inventory(self) -> ActionResult:
        script = r"""
$mods = Get-Module -ListAvailable | Select-Object Name, Version, ModuleBase | Sort-Object Name, Version -Descending
$latest = @()
foreach ($grp in ($mods | Group-Object Name)) {
  $latest += ($grp.Group | Select-Object -First 1)
}
$out = [pscustomobject]@{
  modules = ($latest | Sort-Object Name | ForEach-Object {
    [pscustomobject]@{
      name = $_.Name
      version = $_.Version.ToString()
      path = $_.ModuleBase
    }
  })
  count = ($latest | Measure-Object).Count
}
"""
        return self._ps(script, timeout_seconds=60)

    def _health_check(self, params: dict[str, Any]) -> ActionResult:
        required_modules = _as_list(params.get("required_modules")) or DEFAULT_REQUIRED_MODULES
        required_modules = [str(m).strip() for m in required_modules if str(m).strip()]
        required_modules = [m for m in required_modules if _is_safe_module_name(m)]
        required_modules = required_modules[:50]

        allow_install = self._allow_module_install()

        script = r"""
function AsArray($v) {
  if ($null -eq $v) { return @() }
  if ($v -is [System.Array]) { return $v }
  return @($v)
}

$id = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object System.Security.Principal.WindowsPrincipal($id)
$isAdmin = $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)

$cs = Get-CimInstance Win32_ComputerSystem
$partOfDomain = [bool]$cs.PartOfDomain
$domainName = if ($partOfDomain) { [string]$cs.Domain } else { $null }

$dc = $null
$dcOk = $false
$dcRaw = $null
if ($domainName) {
  try {
    $dcRaw = (& nltest /dsgetdc:$domainName 2>&1 | Out-String).Trim()
    $dcOk = ($LASTEXITCODE -eq 0)
    if ($dcOk) {
      $m = [regex]::Match($dcRaw, 'DC:\s+\\\\(?<name>[A-Za-z0-9_.-]+)')
      if ($m.Success) { $dc = $m.Groups['name'].Value }
    }
  } catch {
    $dcOk = $false
  }
}

$srv = @()
if ($domainName) {
  try {
    $srv = Resolve-DnsName -Name ("_ldap._tcp.dc._msdcs." + $domainName) -Type SRV -ErrorAction Stop |
      Select-Object -First 5 NameTarget, Port, Priority, Weight
  } catch {
    $srv = @()
  }
}

$req = AsArray($params.required_modules)
$installed = @()
$missing = @()
foreach ($m in $req) {
  try {
    $hit = Get-Module -ListAvailable -Name $m | Select-Object -First 1 Name, Version, ModuleBase
    if ($hit) {
      $installed += [pscustomobject]@{ name = $hit.Name; version = $hit.Version.ToString(); path = $hit.ModuleBase }
    } else {
      $missing += [string]$m
    }
  } catch {
    $missing += [string]$m
  }
}

$installAttempts = @()
if ($missing.Count -gt 0 -and [bool]$params.allow_module_install) {
  foreach ($m in $missing) {
    try {
      Install-Module -Name $m -Scope CurrentUser -Force -AllowClobber -ErrorAction Stop | Out-Null
      $installAttempts += [pscustomobject]@{ name = $m; ok = $true; error = $null }
    } catch {
      $installAttempts += [pscustomobject]@{ name = $m; ok = $false; error = $_.Exception.Message }
    }
  }
  # Re-check after install.
  $installed = @()
  $missing2 = @()
  foreach ($m in $req) {
    $hit = $null
    try { $hit = Get-Module -ListAvailable -Name $m | Select-Object -First 1 Name, Version, ModuleBase } catch { $hit = $null }
    if ($hit) {
      $installed += [pscustomobject]@{ name = $hit.Name; version = $hit.Version.ToString(); path = $hit.ModuleBase }
    } else {
      $missing2 += [string]$m
    }
  }
  $missing = $missing2
}

$out = [pscustomobject]@{
  timestamp = (Get-Date).ToUniversalTime().ToString('o')
  powershell = [pscustomobject]@{
    ps_version = $PSVersionTable.PSVersion.ToString()
    edition = $PSVersionTable.PSEdition
  }
  admin = [pscustomobject]@{ is_admin = $isAdmin }
  domain = [pscustomobject]@{ part_of_domain = $partOfDomain; domain = $domainName }
  dc = [pscustomobject]@{ ok = $dcOk; dc_name = $dc; raw = $dcRaw; dns_srv = $srv }
  modules = [pscustomobject]@{
    required = $req
    installed = $installed
    missing = $missing
    allow_module_install = [bool]$params.allow_module_install
    install_attempts = $installAttempts
  }
}
"""

        action = self._ps(
            script,
            params={"required_modules": required_modules, "allow_module_install": allow_install},
            timeout_seconds=300 if allow_install else 60,
        )
        if not action.ok or not isinstance(action.result, dict):
            return action

        report = action.result

        # Enrich with pwsh version if available.
        runner = self._runner()
        pwsh_path = None
        pwsh_version = None
        if runner.is_available() and runner.executable == "pwsh":
            pwsh_path = runner.executable_path()
            pwsh_version = str((report.get("powershell") or {}).get("ps_version") or "")
        else:
            # Probe pwsh even if using Windows PowerShell.
            probe = PowerShellRunner(executable="pwsh")
            if probe.is_available():
                ver = probe.run_json("$out = $PSVersionTable.PSVersion.ToString()", params={})
                if ver.ok and isinstance(ver.data, str):
                    pwsh_version = ver.data
                pwsh_path = probe.executable_path()

        report["pwsh"] = {"present": bool(pwsh_path), "path": pwsh_path, "version": pwsh_version}

        # Compute a simple score out of 100.
        score = 0
        checks = []

        pwsh_present = bool(report.get("pwsh", {}).get("present"))
        checks.append({"id": "pwsh.present", "ok": pwsh_present})
        score += 25 if pwsh_present else 0

        major_ok = False
        try:
            major = int(str(pwsh_version or "").split(".", 1)[0])
            major_ok = major >= 7
        except Exception:
            major_ok = False
        checks.append({"id": "pwsh.version_major>=7", "ok": major_ok, "value": pwsh_version})
        score += 10 if major_ok else 0

        installed = (report.get("modules") or {}).get("installed") or []
        missing = (report.get("modules") or {}).get("missing") or []
        total = max(1, len(required_modules))
        present_count = max(0, total - len(missing))
        module_score = int((present_count / total) * 25)
        checks.append(
            {"id": "modules.required_present", "ok": len(missing) == 0, "present": present_count, "total": total}
        )
        score += module_score

        is_admin = bool((report.get("admin") or {}).get("is_admin"))
        checks.append({"id": "admin", "ok": is_admin})
        score += 10 if is_admin else 0

        domain_joined = bool((report.get("domain") or {}).get("part_of_domain"))
        checks.append({"id": "domain.joined", "ok": domain_joined, "domain": (report.get("domain") or {}).get("domain")})
        score += 10 if domain_joined else 0

        dc_ok = bool((report.get("dc") or {}).get("ok"))
        checks.append({"id": "dc.connectivity", "ok": dc_ok, "dc_name": (report.get("dc") or {}).get("dc_name")})
        score += 20 if dc_ok else 0

        report["score"] = score
        report["checks"] = checks
        report["allow_module_install"] = allow_install
        return ActionResult(ok=True, result=report, stdout=action.stdout, stderr=action.stderr, exit_code=0)

    def _query_eventlog(self, params: dict[str, Any]) -> ActionResult:
        log_names = [str(x).strip() for x in _as_list(params.get("log_names")) if str(x).strip()]
        if not log_names:
            return ActionResult(ok=False, stderr="log_names is required", exit_code=2)
        log_names = log_names[:20]

        levels_raw = _as_list(params.get("levels"))
        providers = [str(x).strip() for x in _as_list(params.get("providers")) if str(x).strip()][:50]
        event_ids = []
        for x in _as_list(params.get("event_ids")):
            try:
                event_ids.append(int(x))
            except Exception:
                continue
        event_ids = event_ids[:100]

        lookback_hours = max(1, min(24 * 30, _as_int(params.get("lookback_hours"), 24)))
        max_events = max(1, min(5000, _as_int(params.get("max_events"), 200)))

        level_map = {
            "critical": 1,
            "crit": 1,
            "error": 2,
            "err": 2,
            "warning": 3,
            "warn": 3,
            "information": 4,
            "info": 4,
            "verbose": 5,
        }
        levels = []
        for entry in levels_raw:
            if entry is None:
                continue
            if isinstance(entry, int):
                if 1 <= entry <= 5:
                    levels.append(entry)
                continue
            text = str(entry).strip().lower()
            if not text:
                continue
            if text.isdigit():
                num = int(text)
                if 1 <= num <= 5:
                    levels.append(num)
                continue
            if text in level_map:
                levels.append(level_map[text])
        levels = sorted(set(levels))[:5]

        script = r"""
function AsArray($v) {
  if ($null -eq $v) { return @() }
  if ($v -is [System.Array]) { return $v }
  return @($v)
}

$logNames = AsArray($params.log_names)
$levels = AsArray($params.levels)
$providers = AsArray($params.providers)
$eventIds = AsArray($params.event_ids)
$lookback = [int]$params.lookback_hours
$maxEvents = [int]$params.max_events
$start = (Get-Date).AddHours(-1 * $lookback)

$errors = @()
$events = @()
$remaining = $maxEvents
foreach ($log in $logNames) {
  if ($remaining -le 0) { break }
  try {
    $filter = @{ LogName = $log; StartTime = $start }
    if ($levels.Count -gt 0) { $filter.Level = $levels }
    if ($providers.Count -gt 0) { $filter.ProviderName = $providers }
    if ($eventIds.Count -gt 0) { $filter.Id = $eventIds }
    $batch = Get-WinEvent -FilterHashtable $filter -MaxEvents $remaining -ErrorAction Stop
    $events += $batch
    $remaining = $maxEvents - ($events | Measure-Object).Count
  } catch {
    $errors += [pscustomobject]@{ log = $log; error = $_.Exception.Message }
  }
}

$items = $events | Sort-Object TimeCreated -Descending | Select-Object -First $maxEvents | ForEach-Object {
  $msg = $null
  try { $msg = $_.Message } catch { $msg = $null }
  if ($msg -and $msg.Length -gt 2000) { $msg = $msg.Substring(0, 2000) + "…" }
  [pscustomobject]@{
    time_utc = ($_.TimeCreated.ToUniversalTime().ToString('o'))
    id = $_.Id
    level = $_.LevelDisplayName
    provider = $_.ProviderName
    log_name = $_.LogName
    record_id = $_.RecordId
    machine = $_.MachineName
    message = $msg
  }
}

$out = [pscustomobject]@{
  query = [pscustomobject]@{
    log_names = $logNames
    levels = $levels
    providers = $providers
    event_ids = $eventIds
    lookback_hours = $lookback
    max_events = $maxEvents
  }
  items = $items
  count = ($items | Measure-Object).Count
  errors = $errors
}
"""
        return self._ps(
            script,
            params={
                "log_names": log_names,
                "levels": levels,
                "providers": providers,
                "event_ids": event_ids,
                "lookback_hours": lookback_hours,
                "max_events": max_events,
            },
            timeout_seconds=120,
        )

    def _query_registry(self, params: dict[str, Any]) -> ActionResult:
        hive = str(params.get("hive") or "").strip().upper()
        path = str(params.get("path") or "").strip()
        value_name = params.get("value_name")
        value_name = str(value_name).strip() if value_name is not None else None
        recursive = _parse_bool(params.get("recursive"))
        max_items = max(1, min(5000, _as_int(params.get("max_items"), 200)))

        if hive not in ("HKLM", "HKCU", "HKCR", "HKU", "HKCC"):
            return ActionResult(ok=False, stderr="hive must be one of HKLM/HKCU/HKCR/HKU/HKCC", exit_code=2)
        if not path:
            return ActionResult(ok=False, stderr="path is required", exit_code=2)

        script = r"""
function NormalizeHive($h) {
  switch ($h) {
    "HKLM" { return "HKLM:" }
    "HKCU" { return "HKCU:" }
    "HKCR" { return "HKCR:" }
    "HKU"  { return "HKU:" }
    "HKCC" { return "HKCC:" }
    default { throw "invalid hive" }
  }
}

$hive = NormalizeHive([string]$params.hive)
$sub = [string]$params.path
$full = Join-Path $hive $sub
if (-not (Test-Path -LiteralPath $full)) {
  throw ("registry path not found: " + $full)
}

$valueName = $params.value_name
$recursive = [bool]$params.recursive
$max = [int]$params.max_items

if ($valueName) {
  $p = Get-ItemProperty -LiteralPath $full -Name $valueName -ErrorAction Stop
  $out = [pscustomobject]@{
    hive = $params.hive
    path = $params.path
    value_name = [string]$valueName
    value = $p.$valueName
  }
} elseif ($recursive) {
  $keys = Get-ChildItem -LiteralPath $full -Recurse -ErrorAction SilentlyContinue | Select-Object -First $max
  $out = [pscustomobject]@{
    hive = $params.hive
    path = $params.path
    recursive = $true
    keys = ($keys | ForEach-Object { $_.Name })
    count = ($keys | Measure-Object).Count
  }
} else {
  $p = Get-ItemProperty -LiteralPath $full -ErrorAction Stop
  $items = @()
  foreach ($prop in ($p.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS(.*)$' })) {
    $items += [pscustomobject]@{ name = $prop.Name; value = $prop.Value }
    if ($items.Count -ge $max) { break }
  }
  $out = [pscustomobject]@{
    hive = $params.hive
    path = $params.path
    values = $items
    count = $items.Count
  }
}
"""
        return self._ps(
            script,
            params={
                "hive": hive,
                "path": path,
                "value_name": value_name,
                "recursive": recursive,
                "max_items": max_items,
            },
            timeout_seconds=60,
        )

    def _query_files(self, params: dict[str, Any]) -> ActionResult:
        allowed_roots = [str(x).strip() for x in _as_list(params.get("allowed_roots")) if str(x).strip()]
        rel_path = str(params.get("path") or "").strip()
        glob = str(params.get("glob") or "").strip() or None
        max_depth = max(0, min(20, _as_int(params.get("max_depth"), 4)))
        max_items = max(1, min(20_000, _as_int(params.get("max_items"), 500)))
        include_hidden = _parse_bool(params.get("include_hidden"))

        if not allowed_roots:
            return ActionResult(ok=False, stderr="allowed_roots is required", exit_code=2)

        script = r"""
function AsArray($v) {
  if ($null -eq $v) { return @() }
  if ($v -is [System.Array]) { return $v }
  return @($v)
}

function ResolveFull($p) {
  try {
    return (Resolve-Path -LiteralPath $p -ErrorAction Stop).Path
  } catch {
    return $null
  }
}

$roots = AsArray($params.allowed_roots) | Where-Object { $_ }
$path = [string]$params.path
$glob = $params.glob
$maxDepth = [int]$params.max_depth
$maxItems = [int]$params.max_items
$includeHidden = [bool]$params.include_hidden

$resolvedRoots = @()
foreach ($r in $roots) {
  $full = ResolveFull([string]$r)
  if ($full) { $resolvedRoots += $full }
}
if ($resolvedRoots.Count -eq 0) { throw "no valid allowed_roots" }

function InRoot($fullPath) {
  foreach ($r in $resolvedRoots) {
    if ($fullPath.StartsWith($r, [System.StringComparison]::OrdinalIgnoreCase)) { return $r }
  }
  return $null
}

$target = $null
if ($path) {
  if ([System.IO.Path]::IsPathRooted($path)) {
    $full = ResolveFull($path)
    if (-not $full) { throw ("path not found: " + $path) }
    $rootHit = InRoot($full)
    if (-not $rootHit) { throw "path is outside allowed_roots" }
    $target = $full
  } else {
    $base = $resolvedRoots[0]
    $joined = Join-Path $base $path
    $full = ResolveFull($joined)
    if (-not $full) { throw ("path not found: " + $joined) }
    $target = $full
  }
} else {
  $target = $resolvedRoots[0]
}

$queue = New-Object System.Collections.Generic.Queue[object]
$queue.Enqueue(@($target, 0))
$items = New-Object System.Collections.Generic.List[object]
$errors = New-Object System.Collections.Generic.List[object]

while ($queue.Count -gt 0 -and $items.Count -lt $maxItems) {
  $pair = $queue.Dequeue()
  $dir = [string]$pair[0]
  $depth = [int]$pair[1]
  try {
    if ($includeHidden) {
      $children = Get-ChildItem -LiteralPath $dir -Force -ErrorAction Stop
    } else {
      $children = Get-ChildItem -LiteralPath $dir -ErrorAction Stop
    }
  } catch {
    $errors.Add([pscustomobject]@{ path = $dir; error = $_.Exception.Message }) | Out-Null
    continue
  }

  foreach ($child in $children) {
    if ($items.Count -ge $maxItems) { break }
    if ($child.PSIsContainer) {
      if ($depth -lt $maxDepth) {
        $queue.Enqueue(@($child.FullName, $depth + 1))
      }
      continue
    }
    if ($glob -and -not ($child.Name -like $glob)) { continue }
    $attrs = [string]$child.Attributes
    $items.Add([pscustomobject]@{
      path = $child.FullName
      name = $child.Name
      size = $child.Length
      mtime_utc = ($child.LastWriteTimeUtc.ToString('o'))
      hidden = ($attrs -match 'Hidden')
      system = ($attrs -match 'System')
    }) | Out-Null
  }
}

$out = [pscustomobject]@{
  resolved_roots = $resolvedRoots
  target = $target
  glob = $glob
  max_depth = $maxDepth
  max_items = $maxItems
  include_hidden = $includeHidden
  items = $items
  count = $items.Count
  errors = $errors
}
"""
        return self._ps(
            script,
            params={
                "allowed_roots": allowed_roots,
                "path": rel_path,
                "glob": glob,
                "max_depth": max_depth,
                "max_items": max_items,
                "include_hidden": include_hidden,
            },
            timeout_seconds=120,
        )

    def _query_processes(self, params: dict[str, Any]) -> ActionResult:
        name_contains = str(params.get("name_contains") or "").strip()
        include_cmdline = _parse_bool(params.get("include_cmdline"))
        max_items = max(1, min(5000, _as_int(params.get("max_items"), 200)))

        script = r"""
$needle = [string]$params.name_contains
$includeCmd = [bool]$params.include_cmdline
$max = [int]$params.max_items

if ($includeCmd) {
  $items = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object { -not $needle -or ($_.Name -like ("*" + $needle + "*")) -or ($_.CommandLine -like ("*" + $needle + "*")) } |
    Select-Object -First $max Name, ProcessId, CommandLine, ExecutablePath, CreationDate |
    ForEach-Object {
      [pscustomobject]@{
        name = $_.Name
        pid = $_.ProcessId
        cmdline = $_.CommandLine
        exe = $_.ExecutablePath
        created = $_.CreationDate
      }
    }
} else {
  $items = Get-Process -ErrorAction SilentlyContinue |
    Where-Object { -not $needle -or ($_.Name -like ("*" + $needle + "*")) } |
    Sort-Object CPU -Descending |
    Select-Object -First $max |
    ForEach-Object {
      $start = $null
      try { $start = $_.StartTime } catch { $start = $null }
      [pscustomobject]@{
        name = $_.Name
        pid = $_.Id
        cpu = $_.CPU
        working_set = $_.WorkingSet64
        start_time = $start
      }
    }
}

$out = [pscustomobject]@{
  query = [pscustomobject]@{ name_contains = $needle; include_cmdline = $includeCmd; max_items = $max }
  items = $items
  count = ($items | Measure-Object).Count
}
"""
        return self._ps(
            script,
            params={"name_contains": name_contains, "include_cmdline": include_cmdline, "max_items": max_items},
            timeout_seconds=60,
        )

    def _query_network_probe(self, params: dict[str, Any]) -> ActionResult:
        dns_name = str(params.get("dns_name") or "").strip() or None
        tcp_host = str(params.get("tcp_host") or "").strip() or None
        tcp_port = _as_int(params.get("tcp_port"), 0)
        ping_host = str(params.get("ping_host") or "").strip() or None
        traceroute_host = str(params.get("traceroute_host") or "").strip() or None

        script = r"""
$outObj = [ordered]@{}

if ($params.dns_name) {
  try {
    $outObj.dns = Resolve-DnsName -Name ([string]$params.dns_name) -ErrorAction Stop |
      Select-Object -First 20 Name, Type, IPAddress, NameHost, TTL
  } catch {
    $outObj.dns = [pscustomobject]@{ ok = $false; error = $_.Exception.Message }
  }
}

if ($params.ping_host) {
  try {
    $host = [string]$params.ping_host
    $probe = Test-Connection -ComputerName $host -Count 1 -ErrorAction Stop
    $outObj.ping = [pscustomobject]@{
      host = $host
      ok = $true
      latency_ms = ($probe | Select-Object -First 1).ResponseTime
      address = ($probe | Select-Object -First 1).Address.IPAddressToString
    }
  } catch {
    $outObj.ping = [pscustomobject]@{ host = [string]$params.ping_host; ok = $false; error = $_.Exception.Message }
  }
}

if ($params.tcp_host -and $params.tcp_port) {
  $host = [string]$params.tcp_host
  $port = [int]$params.tcp_port
  try {
    if (Get-Command Test-NetConnection -ErrorAction SilentlyContinue) {
      $tnc = Test-NetConnection -ComputerName $host -Port $port -WarningAction SilentlyContinue
      $outObj.tcp = [pscustomobject]@{
        host = $host
        port = $port
        ok = [bool]$tnc.TcpTestSucceeded
        remote_address = $tnc.RemoteAddress
        ping_succeeded = $tnc.PingSucceeded
      }
    } else {
      $client = New-Object System.Net.Sockets.TcpClient
      $iar = $client.BeginConnect($host, $port, $null, $null)
      $ok = $iar.AsyncWaitHandle.WaitOne(3000, $false)
      if ($ok) { $client.EndConnect($iar) }
      $client.Close()
      $outObj.tcp = [pscustomobject]@{ host = $host; port = $port; ok = $ok }
    }
  } catch {
    $outObj.tcp = [pscustomobject]@{ host = $host; port = $port; ok = $false; error = $_.Exception.Message }
  }
}

if ($params.traceroute_host) {
  $host = [string]$params.traceroute_host
  try {
    if (Get-Command Test-NetConnection -ErrorAction SilentlyContinue) {
      $trace = Test-NetConnection -ComputerName $host -TraceRoute -WarningAction SilentlyContinue
      $outObj.traceroute = [pscustomobject]@{
        host = $host
        hops = $trace.TraceRoute
      }
    } else {
      $outObj.traceroute = [pscustomobject]@{ host = $host; ok = $false; error = "Test-NetConnection not available" }
    }
  } catch {
    $outObj.traceroute = [pscustomobject]@{ host = $host; ok = $false; error = $_.Exception.Message }
  }
}

$out = [pscustomobject]$outObj
"""
        return self._ps(
            script,
            params={
                "dns_name": dns_name,
                "tcp_host": tcp_host,
                "tcp_port": tcp_port if tcp_port else None,
                "ping_host": ping_host,
                "traceroute_host": traceroute_host,
            },
            timeout_seconds=120,
        )

    def _evidence_bundle(self, params: dict[str, Any]) -> ActionResult:
        store = AgentTokenStore()
        state_dir = store.state_dir
        evidence_dir = state_dir / "evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)

        allowed_roots = [Path(str(x)).expanduser().resolve() for x in _as_list(params.get("allowed_roots")) if x]
        if not allowed_roots:
            allowed_roots = [state_dir.resolve()]

        include_paths = [Path(str(x)).expanduser() for x in _as_list(params.get("paths")) if x]
        include_paths = include_paths[:50]

        bundle_id = secrets.token_hex(8)
        bundle_path = evidence_dir / f"evidence-{bundle_id}.zip"

        manifest: dict[str, Any] = {
            "generated_at": _now_iso(),
            "bundle_id": bundle_id,
            "state_dir": str(state_dir),
            "included": [],
        }

        def is_allowed(path: Path) -> bool:
            try:
                resolved = path.resolve()
            except Exception:
                return False
            for root in allowed_roots:
                try:
                    if str(resolved).lower().startswith(str(root).lower()):
                        return True
                except Exception:
                    continue
            return False

        def add_file(zf: zipfile.ZipFile, path: Path, arcname: str, *, tail_max: int | None = None) -> None:
            try:
                if not path.exists() or not path.is_file():
                    return
                # Never include secrets.
                if path.name == "agent_token":
                    return
                if tail_max:
                    zf.writestr(arcname, _tail_bytes(path, tail_max))
                else:
                    zf.write(path, arcname=arcname)
                manifest["included"].append({"path": str(path), "arcname": arcname})
            except Exception:
                return

        with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            add_file(zf, state_dir / "agent.log.jsonl", "agent.log.jsonl", tail_max=2_000_000)
            add_file(zf, state_dir / "job_results.jsonl", "job_results.jsonl", tail_max=2_000_000)
            add_file(zf, state_dir / "last_job_result.json", "last_job_result.json", tail_max=200_000)

            for extra in include_paths:
                if not is_allowed(extra):
                    continue
                add_file(zf, extra, f"extras/{extra.name}")

            zf.writestr("manifest.json", json.dumps(manifest, indent=2, default=str).encode("utf-8"))

        return ActionResult(ok=True, result={"bundle_path": str(bundle_path), "manifest": manifest}, artifacts=[bundle_path])
