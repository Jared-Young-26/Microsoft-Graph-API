from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from microsoft import PowerShellModuleClient, is_powershell_envelope, unwrap_powershell_data


TIME_SKEW_DEFAULT_MINUTES = 5


def _iso_now():
    """Internal helper for iso now."""
    return datetime.now(timezone.utc).isoformat()


def _wrap_envelope(result, payload_builder):
    """Internal helper for wrap envelope."""
    if is_powershell_envelope(result):
        if not result.get("ok", True):
            return result
        data = unwrap_powershell_data(result)
        payload = payload_builder(data, result.get("meta") or {})
        return {**result, "data": payload}
    return payload_builder(result, {})


def _ensure_list(value):
    """Ensure list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _text(value, fallback=""):
    """Internal helper for text."""
    if value is None:
        return fallback
    return str(value)


def _bool(value):
    """Internal helper for bool."""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).lower() in ("true", "1", "yes", "ok")


def _guidance_block(summary, observed, why, likely_cause, next_checks, limitations):
    """Internal helper for guidance block."""
    return {
        "summary": summary,
        "observed": observed,
        "why": why,
        "likely_cause": likely_cause,
        "next_checks": next_checks,
        "limitations": limitations,
    }


def _build_guidance_endpoint_auth(evidence: dict, skew_warn_minutes: int):
    """Build guidance endpoint auth."""
    observed = []
    next_checks = []
    limitations = []

    logged_on = evidence.get("logged_on_users") or []
    kerberos = evidence.get("kerberos") or {}
    secure_channel = evidence.get("secure_channel") or {}
    time_sync = evidence.get("time_sync") or {}
    last_auth = evidence.get("last_auth") or {}
    errors = evidence.get("errors") or []

    ticket_count = kerberos.get("ticket_count")
    if ticket_count is None:
        limitations.append("Kerberos ticket status unavailable.")
    elif int(ticket_count) == 0:
        observed.append({
            "text": "No Kerberos tickets were detected for the current session.",
            "evidence_keys": ["kerberos.ticket_count"],
        })
        next_checks.append("Verify the user can obtain Kerberos tickets (klist) and re-authenticate.")

    secure_ok = secure_channel.get("ok")
    if secure_ok is None:
        limitations.append("Secure channel status could not be evaluated.")
    elif not _bool(secure_ok):
        observed.append({
            "text": "Secure channel to the domain is broken or unhealthy.",
            "evidence_keys": ["secure_channel.ok", "secure_channel.detail"],
        })
        next_checks.append("Verify machine account trust and reset secure channel if needed.")

    offset_ms = time_sync.get("offset_ms")
    dc_offset_ms = time_sync.get("dc_offset_ms")
    warn_ms = (skew_warn_minutes or TIME_SKEW_DEFAULT_MINUTES) * 60 * 1000
    if offset_ms is None and dc_offset_ms is None:
        limitations.append("Time sync offset could not be measured.")
    else:
        max_offset = None
        if offset_ms is not None:
            max_offset = abs(float(offset_ms))
        if dc_offset_ms is not None:
            max_offset = max(max_offset or 0, abs(float(dc_offset_ms)))
        if max_offset is not None and max_offset > warn_ms:
            observed.append({
                "text": f"Time skew exceeds {skew_warn_minutes} minutes.",
                "evidence_keys": ["time_sync.offset_ms", "time_sync.dc_offset_ms"],
            })
            next_checks.append("Confirm NTP source and resync system time.")

    if not logged_on:
        limitations.append("Logged-on user list unavailable.")
    if not last_auth:
        limitations.append("Last successful authentication not available (Security log access).")

    likely = {
        "text": "Authentication state appears healthy on this endpoint.",
        "confidence": "low",
        "evidence_keys": [],
    }
    if any(item for item in observed if "Time skew" in item["text"]):
        likely = {
            "text": "Time skew is likely preventing Kerberos authentication.",
            "confidence": "high",
            "evidence_keys": ["time_sync.offset_ms", "time_sync.dc_offset_ms"],
        }
    elif any(item for item in observed if "Secure channel" in item["text"]):
        likely = {
            "text": "Machine trust issue may be blocking authentication.",
            "confidence": "medium",
            "evidence_keys": ["secure_channel.ok"],
        }
    elif any(item for item in observed if "Kerberos tickets" in item["text"]):
        likely = {
            "text": "Kerberos tickets are missing or expired on the endpoint.",
            "confidence": "medium",
            "evidence_keys": ["kerberos.ticket_count"],
        }

    if errors:
        limitations.append("Some checks returned errors; see evidence for details.")

    summary = (
        "Endpoint authentication health checks completed."
        if not observed
        else "Endpoint authentication anomalies detected."
    )
    why = (
        "Kerberos and secure channel health are required for domain authentication. "
        "Time skew beyond the Kerberos window or a broken secure channel can cause login failures "
        "even when directory permissions are correct."
    )

    return _guidance_block(summary, observed, why, likely, next_checks, limitations)


def _build_guidance_policy(evidence: dict, lookback_hours: int):
    """Build guidance policy."""
    observed = []
    next_checks = []
    limitations = []

    applied = evidence.get("applied_policy_summary") or {}
    failures = evidence.get("policy_failure_events") or []
    drift = evidence.get("policy_drift_indicators") or {}
    overrides_detected = drift.get("overrides_detected")

    last_refresh = applied.get("last_refresh")
    if failures:
        observed.append({
            "text": f"{len(failures)} policy processing errors were recorded in the last {lookback_hours}h.",
            "evidence_keys": ["policy_failure_events"],
        })
        next_checks.append("Review GroupPolicy operational events for the failure codes.")
    if overrides_detected:
        observed.append({
            "text": "Local policy overrides were detected on the endpoint.",
            "evidence_keys": ["policy_drift_indicators.overrides_detected"],
        })
        next_checks.append("Inspect local policy registry overrides for unexpected settings.")

    if not applied:
        limitations.append("Applied GPO list unavailable (gpresult).")
    if not last_refresh:
        limitations.append("Last policy refresh time not available.")

    likely = {
        "text": "Policy application appears consistent on this endpoint.",
        "confidence": "low",
        "evidence_keys": [],
    }
    if failures:
        likely = {
            "text": "Group Policy processing errors are likely causing the drift.",
            "confidence": "medium",
            "evidence_keys": ["policy_failure_events"],
        }
    elif overrides_detected:
        likely = {
            "text": "Local policy overrides may be superseding domain intent.",
            "confidence": "medium",
            "evidence_keys": ["policy_drift_indicators.overrides_detected"],
        }

    summary = "Effective policy review completed." if not observed else "Policy drift indicators detected."
    why = (
        "Group Policy intent is defined in AD, but enforcement happens on the endpoint. "
        "Failures or local overrides can cause behavior that differs from expected policy."
    )

    return _guidance_block(summary, observed, why, likely, next_checks, limitations)


def _build_guidance_service_integrity(evidence: dict):
    """Build guidance service integrity."""
    observed = []
    next_checks = []
    limitations = []

    anomalies = evidence.get("unexpected_process_conditions") or []
    restarts = evidence.get("restart_anomalies") or {}

    if anomalies:
        observed.append({
            "text": f"{len(anomalies)} services show a process mismatch or missing process.",
            "evidence_keys": ["unexpected_process_conditions"],
        })
        next_checks.append("Inspect service configuration and process ownership for mismatches.")

    if restarts.get("failure_count", 0) > 0:
        observed.append({
            "text": "Recent service failures were detected in the System log.",
            "evidence_keys": ["restart_anomalies"],
        })
        next_checks.append("Review recent Service Control Manager events for failure causes.")

    if evidence.get("service_process_map") is None:
        limitations.append("Service/process mapping unavailable.")

    likely = {
        "text": "Service/process integrity appears normal.",
        "confidence": "low",
        "evidence_keys": [],
    }
    if anomalies:
        likely = {
            "text": "Services are not aligned with expected runtime processes.",
            "confidence": "medium",
            "evidence_keys": ["unexpected_process_conditions"],
        }

    summary = "Service integrity review completed." if not observed else "Service/process anomalies detected."
    why = (
        "Services can report as running even when their backing process is misaligned or unhealthy. "
        "Mapping services to processes helps isolate runtime failures that configuration alone misses."
    )

    return _guidance_block(summary, observed, why, likely, next_checks, limitations)


def _build_guidance_failure_causality(evidence: dict, lookback_hours: int):
    """Build guidance failure causality."""
    observed = []
    next_checks = []
    limitations = []

    earliest = evidence.get("earliest_failure_event")
    timeline = evidence.get("failure_timeline") or []

    if earliest:
        observed.append({
            "text": "An earliest failure event was identified in the local logs.",
            "evidence_keys": ["earliest_failure_event"],
        })
        next_checks.append("Inspect the earliest failure event and any adjacent events for root cause.")
    elif timeline:
        observed.append({
            "text": "Recent failure events were collected, but a clear earliest event was not identified.",
            "evidence_keys": ["failure_timeline"],
        })
    else:
        limitations.append("No failure events were returned in the selected time window.")

    summary = (
        "Failure causality scan completed."
        if observed
        else "No recent failures were detected in local logs."
    )
    why = (
        "Local event logs preserve the earliest failure that triggered a cascade. "
        "Finding the first error reduces guesswork when later symptoms are noisy."
    )
    likely = {
        "text": "Likely cause is tied to the earliest failure event detected.",
        "confidence": "medium" if earliest else "low",
        "evidence_keys": ["earliest_failure_event"] if earliest else [],
    }
    next_checks.append(f"Expand the search window beyond {lookback_hours}h if the issue predates the timeline.")

    return _guidance_block(summary, observed, why, likely, next_checks, limitations)


def _build_guidance_network_path(evidence: dict, target_host: str):
    """Build guidance network path."""
    observed = []
    next_checks = []
    limitations = []

    dns = evidence.get("dns_resolution_status") or {}
    routes = evidence.get("route_conflicts") or {}
    firewall = evidence.get("firewall_context") or {}
    smb = evidence.get("protocol_session_state") or {}

    if dns.get("status") == "failed":
        observed.append({
            "text": f"DNS resolution failed for {target_host} on the endpoint.",
            "evidence_keys": ["dns_resolution_status"],
        })
        next_checks.append("Verify DNS servers configured on the endpoint and resolve the hostname.")
    if routes.get("has_conflict"):
        observed.append({
            "text": "Multiple default routes detected; routing ambiguity possible.",
            "evidence_keys": ["route_conflicts"],
        })
        next_checks.append("Confirm interface metrics and expected default gateway order.")
    if firewall.get("blocked"):
        observed.append({
            "text": "Firewall profiles indicate inbound or outbound blocking.",
            "evidence_keys": ["firewall_context"],
        })
        next_checks.append("Review firewall profile state and default actions on the endpoint.")
    if smb.get("session_count") == 0 and target_host:
        next_checks.append("If SMB is required, attempt a fresh connection and confirm port 445 reachability.")

    if not dns:
        limitations.append("DNS resolution results not available.")
    if not firewall:
        limitations.append("Firewall profile status not available.")

    summary = (
        f"Host perspective network checks completed for {target_host}."
        if observed
        else f"No obvious host-side network blockers detected for {target_host}."
    )
    why = (
        "Routing tables, DNS configuration, and local firewall state can cause a single host to fail "
        "even when the wider network appears healthy."
    )
    likely = {
        "text": "Host-side configuration appears healthy." if not observed else "Host-side configuration likely contributing to reachability issues.",
        "confidence": "low" if not observed else "medium",
        "evidence_keys": [],
    }

    return _guidance_block(summary, observed, why, likely, next_checks, limitations)


class RemoteWorkflowClient:
    """Client for Remote Workflow operations."""
    def __init__(self, powershell=None):
        """Initialize the instance."""
        self._powershell = powershell or PowerShellModuleClient().session

    def _get_powershell(self):
        """Get powershell."""
        if isinstance(self._powershell, PowerShellModuleClient):
            return self._powershell
        return PowerShellModuleClient(session=self._powershell)

    def _build_output(self, workflow_id: str, name: str, purpose: str, evidence: dict, guidance: dict, meta: dict):
        """Build output."""
        return {
            "workflow": {
                "id": workflow_id,
                "name": name,
                "purpose": purpose,
                "captured_at": _iso_now(),
            },
            "summary": {
                "status": "warn" if guidance.get("observed") else "ok",
                "headline": guidance.get("summary"),
                "evidence": evidence.get("summary_evidence", []),
            },
            "guidance": guidance,
            "evidence": evidence,
            "meta": {
                "target": (meta or {}).get("ssh", {}).get("host"),
                "transport": (meta or {}).get("ssh", {}).get("transport"),
                "duration_ms": (meta or {}).get("ssh", {}).get("duration_ms"),
            },
        }

    def endpoint_auth_reality(self, lookback_hours=24, time_skew_warn_minutes=TIME_SKEW_DEFAULT_MINUTES):
        """Run endpoint auth reality."""
        script = r"""
        $errors = @()
        $loggedOnUsers = @()
        try {
          $raw = (quser 2>&1 | Out-String)
          $lines = $raw -split "`r?`n" | Where-Object { $_.Trim() -ne '' }
          if ($lines.Count -gt 1) {
            $lines = $lines | Select-Object -Skip 1
            foreach ($line in $lines) {
              $parts = $line -split "\s+"
              if ($parts.Count -ge 3) {
                $loggedOnUsers += [PSCustomObject]@{
                  user = $parts[0]
                  session = $parts[1]
                  state = $parts[3]
                }
              }
            }
          }
        } catch {
          $errors += [PSCustomObject]@{ source = 'quser'; message = $_.Exception.Message }
        }
        if (-not $loggedOnUsers -or $loggedOnUsers.Count -eq 0) {
          try {
            $sessions = Get-CimInstance Win32_LoggedOnUser | ForEach-Object { $_.Antecedent }
            foreach ($s in $sessions) {
              $loggedOnUsers += [PSCustomObject]@{ user = $s.Name; session = 'CIM'; state = '' }
            }
          } catch {
            $errors += [PSCustomObject]@{ source = 'Win32_LoggedOnUser'; message = $_.Exception.Message }
          }
        }

        $klistRaw = ''
        $ticketCount = 0
        $defaultPrincipal = $null
        $ticketExpiries = @()
        try {
          $klistRaw = (klist 2>&1 | Out-String)
          $lines = $klistRaw -split "`r?`n"
          foreach ($line in $lines) {
            if ($line -match 'Default Principal:\s*(.+)$') { $defaultPrincipal = $matches[1].Trim() }
            if ($line -match 'End Time:\s*(.+)$') { $ticketExpiries += $matches[1].Trim() }
          }
          $ticketCount = ($lines | Where-Object { $_ -match 'krbtgt' }).Count
        } catch {
          $errors += [PSCustomObject]@{ source = 'klist'; message = $_.Exception.Message }
        }

        $secureChannel = [PSCustomObject]@{ ok = $null; detail = $null }
        try {
          $sc = Test-ComputerSecureChannel -Verbose -ErrorAction Stop
          $secureChannel.ok = [bool]$sc
          $secureChannel.detail = $sc
        } catch {
          $secureChannel.ok = $false
          $secureChannel.detail = $_.Exception.Message
        }

        $timeStatusRaw = ''
        $timeSource = $null
        $offsetMs = $null
        try {
          $timeStatusRaw = (w32tm /query /status 2>&1 | Out-String)
          if ($timeStatusRaw -match 'Source:\s*(.+)$') { $timeSource = $matches[1].Trim() }
          if ($timeStatusRaw -match 'Offset:\s*([\-0-9\.]+)s') { $offsetMs = [math]::Round([double]$matches[1] * 1000, 1) }
        } catch {
          $errors += [PSCustomObject]@{ source = 'w32tm_status'; message = $_.Exception.Message }
        }

        $dcOffsetMs = $null
        $dcName = $null
        try {
          $monitorRaw = (w32tm /monitor 2>&1 | Out-String)
          if ($monitorRaw -match '^(\\\\[^\s]+)') { $dcName = $matches[1].Trim() }
          if ($monitorRaw -match 'Offset:\s*([\-0-9\.]+)s') { $dcOffsetMs = [math]::Round([double]$matches[1] * 1000, 1) }
        } catch {
          $errors += [PSCustomObject]@{ source = 'w32tm_monitor'; message = $_.Exception.Message }
        }

        $lastAuth = $null
        try {
          $evt = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624} -MaxEvents 1 -ErrorAction Stop
          if ($evt) {
            $lastAuth = [PSCustomObject]@{
              time = $evt.TimeCreated
              message = ($evt.Message | Select-Object -First 1)
            }
          }
        } catch {
          $errors += [PSCustomObject]@{ source = 'SecurityLog'; message = $_.Exception.Message }
        }

        [PSCustomObject]@{
          logged_on_users = $loggedOnUsers
          kerberos = [PSCustomObject]@{
            ticket_count = $ticketCount
            default_principal = $defaultPrincipal
            ticket_expiries = $ticketExpiries
            raw = $klistRaw
          }
          secure_channel = $secureChannel
          time_sync = [PSCustomObject]@{
            source = $timeSource
            offset_ms = $offsetMs
            dc_offset_ms = $dcOffsetMs
            dc_name = $dcName
          }
          last_auth = $lastAuth
          errors = $errors
          summary_evidence = @(
            [PSCustomObject]@{ label = 'Logged-on users'; value = $loggedOnUsers.Count },
            [PSCustomObject]@{ label = 'Kerberos tickets'; value = $ticketCount },
            [PSCustomObject]@{ label = 'Time offset (ms)'; value = $offsetMs }
          )
        }
        """
        result = self._get_powershell().run_json(script)
        return _wrap_envelope(
            result,
            lambda data, meta: self._build_output(
                "endpoint_auth_reality",
                "Endpoint authentication reality check",
                "Validate endpoint authentication artifacts (Kerberos, secure channel, time sync).",
                data or {},
                _build_guidance_endpoint_auth(data or {}, int(time_skew_warn_minutes or TIME_SKEW_DEFAULT_MINUTES)),
                meta,
            ),
        )

    def effective_policy_vs_intended(self, lookback_hours=24, max_events=50):
        """Run effective policy vs intended."""
        script = r"""
        $errors = @()
        $gpRaw = ''
        try {
          $gpRaw = (gpresult /r 2>&1 | Out-String)
        } catch {
          $errors += [PSCustomObject]@{ source = 'gpresult'; message = $_.Exception.Message }
        }

        $events = @()
        try {
          $startTime = (Get-Date).AddHours(-1 * [int]$LOOKBACK_HOURS)
          $events = Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-GroupPolicy/Operational'; StartTime=$startTime} -MaxEvents $MAX_EVENTS -ErrorAction Stop |
            Where-Object { $_.LevelDisplayName -in @('Error','Warning') } |
            Select-Object TimeCreated, Id, ProviderName, LevelDisplayName, Message
        } catch {
          $errors += [PSCustomObject]@{ source = 'gpo_events'; message = $_.Exception.Message }
        }

        $policyKeys = @()
        try {
          $policyKeys += Get-ChildItem -Path 'HKLM:\Software\Policies' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name
          $policyKeys += Get-ChildItem -Path 'HKCU:\Software\Policies' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name
        } catch {
          $errors += [PSCustomObject]@{ source = 'policy_registry'; message = $_.Exception.Message }
        }

        [PSCustomObject]@{
          gpresult_raw = $gpRaw
          policy_failure_events = $events
          policy_override_paths = $policyKeys
          errors = $errors
          summary_evidence = @(
            [PSCustomObject]@{ label = 'Policy errors'; value = $events.Count },
            [PSCustomObject]@{ label = 'Override keys'; value = $policyKeys.Count }
          )
        }
        """
        result = self._get_powershell().run_json(
            script,
            parameters={"LOOKBACK_HOURS": lookback_hours, "MAX_EVENTS": max_events},
        )
        def build(data, meta):
            """Run build."""
            summary = {}
            if data and data.get("gpresult_raw"):
                try:
                    from local_endpoint import _parse_gpresult_summary

                    summary = _parse_gpresult_summary(data.get("gpresult_raw"))
                except Exception:
                    summary = {}
            evidence = {
                **(data or {}),
                "applied_policy_summary": summary,
                "policy_drift_indicators": {
                    "overrides_detected": bool((data or {}).get("policy_override_paths")),
                    "override_count": len((data or {}).get("policy_override_paths") or []),
                },
            }
            guidance = _build_guidance_policy(evidence, int(lookback_hours or 24))
            return self._build_output(
                "effective_policy_vs_intended",
                "Effective policy vs intended policy",
                "Compare applied GPOs and local policy state with intended domain policy.",
                evidence,
                guidance,
                meta,
            )
        return _wrap_envelope(result, build)

    def service_process_integrity(self, lookback_hours=24, max_events=25):
        """Run service process integrity."""
        script = r"""
        $errors = @()
        $map = @()
        $anomalies = @()
        try {
          $services = Get-CimInstance Win32_Service | Select-Object Name, DisplayName, State, StartMode, ProcessId, StartName
          foreach ($svc in $services) {
            $proc = $null
            if ($svc.ProcessId -and $svc.ProcessId -ne 0) {
              $proc = Get-Process -Id $svc.ProcessId -ErrorAction SilentlyContinue | Select-Object -First 1 Name, Id, StartTime
            }
            $row = [PSCustomObject]@{
              service = $svc.Name
              display_name = $svc.DisplayName
              state = $svc.State
              start_mode = $svc.StartMode
              start_name = $svc.StartName
              process_id = $svc.ProcessId
              process_name = if ($proc) { $proc.Name } else { $null }
              process_start = if ($proc) { $proc.StartTime } else { $null }
            }
            $map += $row
            if ($svc.State -eq 'Running' -and (-not $proc)) {
              $anomalies += [PSCustomObject]@{
                service = $svc.Name
                issue = 'Running service has no backing process'
              }
            }
          }
        } catch {
          $errors += [PSCustomObject]@{ source = 'service_map'; message = $_.Exception.Message }
        }

        $events = @()
        try {
          $startTime = (Get-Date).AddHours(-1 * [int]$LOOKBACK_HOURS)
          $events = Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=$startTime; Id=@(7031,7034)} -MaxEvents $MAX_EVENTS -ErrorAction Stop |
            Select-Object TimeCreated, Id, ProviderName, LevelDisplayName, Message
        } catch {
          $errors += [PSCustomObject]@{ source = 'service_events'; message = $_.Exception.Message }
        }

        [PSCustomObject]@{
          service_process_map = $map
          unexpected_process_conditions = $anomalies
          restart_anomalies = [PSCustomObject]@{ failure_count = $events.Count; events = $events }
          errors = $errors
          summary_evidence = @(
            [PSCustomObject]@{ label = 'Services mapped'; value = $map.Count },
            [PSCustomObject]@{ label = 'Anomalies'; value = $anomalies.Count }
          )
        }
        """
        result = self._get_powershell().run_json(
            script,
            parameters={"LOOKBACK_HOURS": lookback_hours, "MAX_EVENTS": max_events},
        )
        return _wrap_envelope(
            result,
            lambda data, meta: self._build_output(
                "service_process_integrity",
                "Service-to-process integrity check",
                "Validate running services match expected processes and owners.",
                data or {},
                _build_guidance_service_integrity(data or {}),
                meta,
            ),
        )

    def recent_failure_causality(self, lookback_hours=24, max_events=50):
        """Run recent failure causality."""
        script = r"""
        $errors = @()
        $timeline = @()
        try {
          $startTime = (Get-Date).AddHours(-1 * [int]$LOOKBACK_HOURS)
          $timeline = Get-WinEvent -FilterHashtable @{LogName=@('System','Application','Security'); StartTime=$startTime; Level=2} -MaxEvents $MAX_EVENTS -ErrorAction Stop |
            Select-Object TimeCreated, LogName, Id, ProviderName, LevelDisplayName, Message
        } catch {
          $errors += [PSCustomObject]@{ source = 'eventlogs'; message = $_.Exception.Message }
        }
        $timeline = $timeline | Sort-Object TimeCreated
        $earliest = $null
        if ($timeline -and $timeline.Count -gt 0) {
          $earliest = $timeline | Select-Object -First 1
        }
        [PSCustomObject]@{
          failure_timeline = $timeline
          earliest_failure_event = $earliest
          correlated_components = ($timeline | Select-Object -ExpandProperty ProviderName -Unique)
          errors = $errors
          summary_evidence = @(
            [PSCustomObject]@{ label = 'Failures collected'; value = $timeline.Count },
            [PSCustomObject]@{ label = 'Earliest failure'; value = if ($earliest) { $earliest.TimeCreated } else { '' } }
          )
        }
        """
        result = self._get_powershell().run_json(
            script,
            parameters={"LOOKBACK_HOURS": lookback_hours, "MAX_EVENTS": max_events},
        )
        return _wrap_envelope(
            result,
            lambda data, meta: self._build_output(
                "recent_failure_causality",
                "Recent failure causality",
                "Locate the earliest local failure event contributing to the issue.",
                data or {},
                _build_guidance_failure_causality(data or {}, int(lookback_hours or 24)),
                meta,
            ),
        )

    def host_network_path_check(self, target_host: str, port: int | None = None):
        """Run host network path check."""
        if not target_host:
            raise ValueError("target_host is required")
        script = r"""
        $errors = @()
        $dns = @()
        try {
          $dns = Resolve-DnsName -Name $TARGET_HOST -ErrorAction Stop | Select-Object Name, Type, IPAddress, TTL
        } catch {
          $errors += [PSCustomObject]@{ source = 'dns'; message = $_.Exception.Message }
        }
        $routes = @()
        try {
          $routes = Get-NetRoute -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue | Select-Object InterfaceAlias, NextHop, RouteMetric
        } catch {
          $errors += [PSCustomObject]@{ source = 'routes'; message = $_.Exception.Message }
        }
        $interfaces = @()
        try {
          $interfaces = Get-NetIPConfiguration | Select-Object InterfaceAlias, IPv4Address, IPv4DefaultGateway, DnsServer
        } catch {
          $errors += [PSCustomObject]@{ source = 'interfaces'; message = $_.Exception.Message }
        }
        $firewall = @()
        try {
          $firewall = Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction
        } catch {
          $errors += [PSCustomObject]@{ source = 'firewall'; message = $_.Exception.Message }
        }
        $smb = @()
        try {
          $smb = Get-SmbConnection | Where-Object { $_.ServerName -eq $TARGET_HOST } | Select-Object ServerName, ShareName, UserName, Dialect
        } catch {
          $errors += [PSCustomObject]@{ source = 'smb'; message = $_.Exception.Message }
        }
        $portTest = $null
        if ($TARGET_PORT) {
          try {
            $portTest = Test-NetConnection -ComputerName $TARGET_HOST -Port $TARGET_PORT -InformationLevel Detailed
          } catch {
            $errors += [PSCustomObject]@{ source = 'port_test'; message = $_.Exception.Message }
          }
        }

        [PSCustomObject]@{
          dns_resolution_status = [PSCustomObject]@{
            status = if ($dns -and $dns.Count -gt 0) { 'ok' } else { 'failed' }
            records = $dns
          }
          routes = $routes
          interfaces = $interfaces
          firewall_profiles = $firewall
          smb_connections = $smb
          port_test = $portTest
          errors = $errors
          summary_evidence = @(
            [PSCustomObject]@{ label = 'DNS records'; value = $dns.Count },
            [PSCustomObject]@{ label = 'Default routes'; value = $routes.Count }
          )
        }
        """
        result = self._get_powershell().run_json(
            script,
            parameters={"TARGET_HOST": target_host, "TARGET_PORT": port},
        )
        def build(data, meta):
            """Run build."""
            routes = data.get("routes") or [] if data else []
            route_conflict = False
            if isinstance(routes, list) and len(routes) > 1:
                route_conflict = True
            firewall_profiles = data.get("firewall_profiles") or [] if data else []
            blocked = any(
                str(item.get("DefaultOutboundAction", "")).lower() == "block"
                for item in firewall_profiles
                if isinstance(item, dict)
            )
            evidence = {
                **(data or {}),
                "route_conflicts": {
                    "has_conflict": route_conflict,
                    "routes": routes,
                },
                "firewall_context": {
                    "profiles": firewall_profiles,
                    "blocked": blocked,
                },
                "protocol_session_state": {
                    "session_count": len(data.get("smb_connections") or []) if data else 0,
                    "sessions": data.get("smb_connections") if data else [],
                },
            }
            guidance = _build_guidance_network_path(evidence, target_host)
            return self._build_output(
                "host_network_path_check",
                "Host-perspective network path check",
                "Validate DNS, routing, firewall, and protocol sessions from the host itself.",
                evidence,
                guidance,
                meta,
            )
        return _wrap_envelope(result, build)
