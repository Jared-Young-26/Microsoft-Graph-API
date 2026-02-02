import re

from microsoft import PowerShellModuleClient, is_powershell_envelope, unwrap_powershell_data


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
    for key, value in (params or {}).items():
        if value is None:
            continue
        parts.append(f"-{key} {_ps_value(value)}")
    return (" " + " ".join(parts)) if parts else ""


def _wrap_envelope(result, payload_builder):
    if is_powershell_envelope(result):
        if not result.get("ok", True):
            return result
        data = unwrap_powershell_data(result)
        payload = payload_builder(data)
        return {**result, "data": payload}
    return payload_builder(result)


class LocalDomainControllerClient:
    def __init__(self, powershell=None, powershell_options=None):
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = LocalDomainControllerPowerShellClient(**options)
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

    def _parse_replsummary(self, text):
        lines = str(text or "").splitlines()
        rows = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(("Source DSA", "Destination DSA", "----")):
                continue
            if "largest delta" in stripped.lower():
                continue
            if "fails/total" in stripped.lower():
                continue
            match = re.match(
                r"^(?P<dc>\S+)\s+(?P<largest_delta>[\w:\.]+)\s+(?P<fails>\d+)\s*/\s*(?P<total>\d+)\s+(?P<percent>\d+)%",
                stripped,
            )
            if match:
                data = match.groupdict()
                fails = int(data["fails"])
                total = int(data["total"])
                rows.append(
                    {
                        "dc": data["dc"],
                        "largest_delta": data["largest_delta"],
                        "failures": fails,
                        "total": total,
                        "success_percent": max(0, 100 - int(data["percent"])),
                        "failure_percent": int(data["percent"]),
                    }
                )
        return rows

    def _parse_fsmo_output(self, text):
        lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
        role_map = {}
        ordered_roles = [
            "Schema master",
            "Domain naming master",
            "PDC",
            "RID pool manager",
            "Infrastructure master",
        ]
        role_index = 0
        for line in lines:
            if line.lower().startswith("the command completed successfully"):
                continue
            if role_index < len(ordered_roles):
                role_map[ordered_roles[role_index]] = line
                role_index += 1
            else:
                role_map[f"Role {role_index + 1}"] = line
                role_index += 1
        return role_map

    def _parse_nltest_dclist(self, text):
        controllers = []
        for line in str(text or "").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            lower = stripped.lower()
            if lower.startswith(("get list", "the command", "flags", "domain", "list of")):
                continue
            match = re.search(r"\\\\?([A-Za-z0-9._-]+)", stripped)
            if not match:
                continue
            hostname = match.group(1)
            controllers.append(
                {
                    "hostname": hostname,
                    "site": None,
                    "ipv4": None,
                    "operating_system": None,
                    "os_version": None,
                    "is_global_catalog": None,
                    "is_read_only": None,
                    "enabled": None,
                    "fsmo_roles": [],
                    "has_fsmo_roles": False,
                    "source": "nltest",
                }
            )
        return controllers

    def _normalize_dc_inventory(self, data):
        if data is None:
            return []
        rows = data if isinstance(data, list) else [data]
        normalized = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            roles = row.get("OperationMasterRoles") or row.get("FsmoRoles") or []
            if isinstance(roles, str):
                roles = [r.strip() for r in roles.split(",") if r.strip()]
            elif isinstance(roles, list):
                roles = [str(r) for r in roles if r]
            normalized.append(
                {
                    "hostname": row.get("HostName") or row.get("Name") or row.get("ComputerObjectDN"),
                    "site": row.get("Site"),
                    "ipv4": row.get("IPv4Address") or row.get("IPv4"),
                    "operating_system": row.get("OperatingSystem"),
                    "os_version": row.get("OperatingSystemVersion"),
                    "is_global_catalog": row.get("IsGlobalCatalog"),
                    "is_read_only": row.get("IsReadOnly"),
                    "enabled": row.get("Enabled"),
                    "fsmo_roles": roles,
                    "has_fsmo_roles": bool(roles),
                    "source": row.get("Source") or "Get-ADDomainController",
                }
            )
        return normalized

    def _parse_dcdiag_output(self, text):
        findings = []
        current_test = None
        for line in str(text or "").splitlines():
            stripped = line.strip()
            lower = stripped.lower()
            if not stripped:
                continue
            test_match = re.search(r"starting test:\s*(.+)", stripped, re.IGNORECASE)
            if test_match:
                current_test = test_match.group(1).strip()
                continue
            if "failed test" in lower:
                findings.append(
                    {
                        "severity": "error",
                        "test": current_test,
                        "message": stripped,
                        "recommendations": self._recommend_dcdiag_followups(stripped, current_test),
                    }
                )
            elif "warning" in lower:
                findings.append(
                    {
                        "severity": "warning",
                        "test": current_test,
                        "message": stripped,
                        "recommendations": self._recommend_dcdiag_followups(stripped, current_test),
                    }
                )
        return findings

    def _parse_w32tm_status(self, text):
        data = {}
        for line in str(text or "").splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if not key:
                continue
            data[key] = value
        phase_offset = data.get("Phase Offset") or data.get("Offset")
        offset_seconds = None
        if phase_offset:
            match = re.search(r"([+-]?\d+(\.\d+)?)s", phase_offset)
            if match:
                try:
                    offset_seconds = float(match.group(1))
                except ValueError:
                    offset_seconds = None
        data["_offset_seconds"] = offset_seconds
        return data

    def _parse_w32tm_monitor(self, text):
        entries = []
        for line in str(text or "").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            match = re.match(r"^(?P<server>[^\s]+)\s+\[(?P<ip>[^\]]+)\]:\s*(?P<rest>.+)$", stripped)
            if not match:
                continue
            server = match.group("server")
            ip = match.group("ip")
            rest = match.group("rest")
            ntp_offset = None
            ntp_match = re.search(r"NTP:\s*([+-]?\d+(\.\d+)?)s", rest)
            if ntp_match:
                try:
                    ntp_offset = float(ntp_match.group(1))
                except ValueError:
                    ntp_offset = None
            stratum = None
            stratum_match = re.search(r"Stratum:\s*(\d+)", rest)
            if stratum_match:
                try:
                    stratum = int(stratum_match.group(1))
                except ValueError:
                    stratum = None
            refid_match = re.search(r"RefID:\s*([^,]+)", rest)
            entries.append(
                {
                    "server": server,
                    "ip": ip,
                    "ntp_offset_seconds": ntp_offset,
                    "stratum": stratum,
                    "ref_id": refid_match.group(1).strip() if refid_match else None,
                    "raw": stripped,
                }
            )
        return entries

    def _evaluate_time_sync_flags(self, status, monitor):
        flags = {"level": "ok", "skew_seconds": None, "anomalies": []}
        offsets = []
        status_offset = status.get("_offset_seconds") if isinstance(status, dict) else None
        if isinstance(status_offset, (int, float)):
            offsets.append(status_offset)
        if isinstance(monitor, list):
            for entry in monitor:
                offset = entry.get("ntp_offset_seconds")
                if isinstance(offset, (int, float)):
                    offsets.append(offset)
        if offsets:
            worst = max(offsets, key=lambda value: abs(value))
            flags["skew_seconds"] = worst
            if abs(worst) > 300:
                flags["level"] = "error"
            elif abs(worst) > 60:
                flags["level"] = "warning"
        source = status.get("Source") if isinstance(status, dict) else ""
        if source:
            lower = str(source).lower()
            if "local cmos" in lower or "free-running" in lower:
                flags["anomalies"].append("Clock source is local (CMOS/free-running).")
            if "vm ic" in lower or "hyper-v" in lower:
                flags["anomalies"].append("Clock source is virtualization integration (check time hierarchy).")
            if "unspecified" in lower or "none" in lower:
                flags["anomalies"].append("Time source is unspecified.")
        if flags["anomalies"] and flags["level"] == "ok":
            flags["level"] = "warning"
        return flags

    def _recommend_dcdiag_followups(self, message, test_name=None):
        text = f"{test_name or ''} {message or ''}".lower()
        recommendations = []
        if "dns" in text:
            recommendations.extend(
                [
                    "Verify DNS service is running on the DC.",
                    "Check zone replication and critical SRV records.",
                    "Run Resolve-DnsName against the DC and forwarders.",
                ]
            )
        if "advertis" in text or "netlogon" in text:
            recommendations.extend(
                [
                    "Check Netlogon service status and DC advertising events.",
                    "Review Directory Service and System event logs.",
                ]
            )
        if "replication" in text or "repl" in text:
            recommendations.extend(
                [
                    "Run repadmin /replsummary to gauge replication health.",
                    "Run repadmin /showrepl on affected DCs.",
                ]
            )
        if "sysvol" in text or "dfsr" in text or "frs" in text:
            recommendations.extend(
                [
                    "Check DFSR/FRS event logs for SYSVOL errors.",
                    "Run dfsrmig /getglobalstate to confirm SYSVOL migration state.",
                ]
            )
        if "services" in text:
            recommendations.append("Confirm AD DS, DNS, and Netlogon services are running.")
        if "time" in text or "w32time" in text:
            recommendations.extend(
                [
                    "Run w32tm /query /status on the DC.",
                    "Run w32tm /monitor to review domain time sources.",
                ]
            )
        if "rid" in text:
            recommendations.append("Verify RID master connectivity and availability.")
        if "kcc" in text:
            recommendations.append("Review KCC topology events and replication topology.")
        if not recommendations:
            recommendations.append("Review dcdiag output and related event logs for more detail.")
        # De-dupe while preserving order.
        deduped = []
        for item in recommendations:
            if item not in deduped:
                deduped.append(item)
        return deduped

    def _normalize_key(self, key):
        return re.sub(r"[^a-z0-9]+", "", str(key or "").lower())

    def _extract_error_code(self, value):
        if value is None:
            return None
        text = str(value)
        match = re.search(r"(\d+)\s*\(0x[0-9a-fA-F]+\)", text)
        if match:
            return int(match.group(1))
        match = re.search(r"\b(\d{3,})\b", text)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        return None

    def _normalize_showrepl_rows(self, rows):
        if not rows:
            return []
        normalized = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            normalized_row = {self._normalize_key(k): v for k, v in row.items()}

            def pick(*keys):
                for key in keys:
                    value = normalized_row.get(self._normalize_key(key))
                    if value not in (None, ""):
                        return value
                return None

            partner = pick("Source DSA", "Partner", "Source Server", "Source DSA Name")
            naming_context = pick("Naming Context", "Partition")
            last_success = pick("Last Success Time", "Last Success")
            last_failure = pick("Last Failure Time", "Last Failure")
            last_attempt = pick("Last Attempt Time", "Last Attempt")
            error_detail = pick(
                "Last Failure Status",
                "Last Failure Result",
                "Last Failure Error",
                "Last Attempt Result",
                "Result",
            )
            error_code = self._extract_error_code(error_detail)

            normalized.append(
                {
                    "partner": partner,
                    "naming_context": naming_context,
                    "last_success": last_success,
                    "last_failure": last_failure,
                    "last_attempt": last_attempt,
                    "error_code": error_code,
                    "error_detail": error_detail,
                    "source": "repadmin_csv",
                }
            )
        return normalized

    def _parse_showrepl_text(self, text):
        entries = []
        current_context = None
        current = None
        for line in str(text or "").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(("DC=", "OU=", "CN=")):
                current_context = stripped
                continue
            partner_match = re.match(r"^(?P<site>[^\\]+)\\\\(?P<partner>[^\\s]+)\s+via", stripped)
            if not partner_match:
                partner_match = re.match(r"^(?P<partner>[^\\s]+)\s+via", stripped)
            if partner_match:
                if current:
                    entries.append(current)
                partner = partner_match.group("partner")
                current = {
                    "partner": partner,
                    "naming_context": current_context,
                    "last_success": None,
                    "last_failure": None,
                    "last_attempt": None,
                    "error_code": None,
                    "error_detail": None,
                    "source": "repadmin_text",
                }
                continue
            if not current:
                continue
            lower = stripped.lower()
            time_match = re.search(r"@\s*(.+)$", stripped)
            timestamp = time_match.group(1).strip() if time_match else None
            if "last success" in lower:
                current["last_success"] = timestamp or current.get("last_success")
            elif "last attempt" in lower and "successful" in lower:
                current["last_success"] = timestamp or current.get("last_success")
            elif "last attempt" in lower and "failed" in lower:
                current["last_failure"] = timestamp or current.get("last_failure")
                error_match = re.search(r"result\s+(.*)$", stripped, re.IGNORECASE)
                error_detail = error_match.group(1).strip() if error_match else stripped
                current["error_detail"] = error_detail
                current["error_code"] = self._extract_error_code(error_detail)
            elif "last failure" in lower:
                current["last_failure"] = timestamp or current.get("last_failure")
        if current:
            entries.append(current)
        return entries

    def get_replication_health_summary(self):
        """Use repadmin /replsummary to quickly spot unhealthy DC replication."""
        result = self._get_powershell().run("repadmin /replsummary")
        return _wrap_envelope(
            result,
            lambda output: {
                "summary": self._parse_replsummary(output or ""),
                "raw_text": output,
            },
        )

    def get_replication_partners_for_dc(self, dc):
        """Use repadmin /showrepl to inspect inbound partners + last replication status for a DC."""
        script = f"""
        $dc = {_ps_value(dc)}
        $raw = repadmin /showrepl $dc /csv 2>&1 | Out-String
        $rows = $raw -split "`r?`n" | Where-Object {{ $_ -and $_.Trim().StartsWith('"') }}
        $parsed = @()
        if ($rows.Count -gt 0) {{
          try {{
            $parsed = $rows | ConvertFrom-Csv
          }} catch {{
            $parsed = @()
          }}
        }}
        [PSCustomObject]@{{
          rows = $parsed
          raw_text = $raw
        }}
        """
        result = self._get_powershell().run_json(script)
        if is_powershell_envelope(result):
            if not result.get("ok", True):
                return result
            payload = unwrap_powershell_data(result) or {}
            rows = payload.get("rows") or []
            raw_text = payload.get("raw_text") or ""
            normalized = self._normalize_showrepl_rows(rows)
            if not normalized:
                normalized = self._parse_showrepl_text(raw_text)
            meta = dict(result.get("meta") or {})
            meta["raw_text"] = raw_text
            return {**result, "data": normalized, "meta": meta}
        return result

    def get_replication_queue_for_dc(self, dc):
        """Use repadmin /queue to review pending replication operations for a DC."""
        cmd = f"repadmin /queue {_ps_value(dc)}"
        result = self._get_powershell().run(cmd)
        return _wrap_envelope(result, lambda output: {"raw_text": output})

    def force_replication_sync_all(self, dc, flags="AdeP", execute=False):
        """Force inter-DC sync (repadmin /syncall). Use only during targeted troubleshooting."""
        if not execute:
            return {
                "ok": False,
                "message": "Set execute=True to run repadmin /syncall (destructive/operational action).",
            }
        flags = str(flags or "").lstrip("/")
        cmd = f"repadmin /syncall {_ps_value(dc)}"
        if flags:
            cmd += f" /{flags}"
        result = self._get_powershell().run(cmd)
        return _wrap_envelope(
            result,
            lambda output: {"executed": True, "command": cmd, "raw_text": output},
        )

    def run_dc_health_checks(self, verbose=False):
        """Run dcdiag health tests for DNS/services/advertising and basic DC sanity."""
        cmd = "dcdiag /v" if verbose else "dcdiag /q"
        result = self._get_powershell().run(cmd)
        return _wrap_envelope(
            result,
            lambda output: {
                "findings": self._parse_dcdiag_output(output or ""),
                "raw_text": output,
                "verbose": bool(verbose),
            },
        )

    def list_domain_controllers_via_nltest(self, domain):
        """List domain controllers discovered for a domain (nltest /dclist)."""
        cmd = f"nltest /dclist:{_ps_quote(domain)}"
        result = self._get_powershell().run(cmd)
        return _wrap_envelope(result, lambda output: {"domain": domain, "raw_text": output})

    def get_current_dc_for_domain(self, domain):
        """Show which DC locator chooses for a domain (nltest /dsgetdc)."""
        cmd = f"nltest /dsgetdc:{_ps_quote(domain)}"
        result = self._get_powershell().run(cmd)
        return _wrap_envelope(result, lambda output: {"domain": domain, "raw_text": output})

    def get_replication_partner_metadata(self, dc=None):
        """Get structured replication partner metadata via ActiveDirectory module."""
        params = {"Target": dc} if dc else {}
        cmd = "Get-ADReplicationPartnerMetadata" + _ps_params(params)
        cmd += " | Select-Object Server,Partner,PartnerType,LastReplicationSuccess,LastReplicationAttempt,LastReplicationResult,ConsecutiveReplicationFailures"
        return self._get_powershell().run_json(cmd)

    def get_replication_failures(self, dc=None):
        """Get active AD replication failures across DCs or for a target DC."""
        params = {"Target": dc} if dc else {}
        cmd = "Get-ADReplicationFailure" + _ps_params(params)
        cmd += " | Select-Object Server,Partner,FirstFailureTime,FailureCount,LastError"
        return self._get_powershell().run_json(cmd)

    def get_replication_queue_operations(self, dc=None):
        """Get queued AD replication operations (Get-ADReplicationQueueOperation)."""
        params = {"Server": dc} if dc else {}
        cmd = "Get-ADReplicationQueueOperation" + _ps_params(params)
        cmd += " | Select-Object Server,OperationType,Partition,QueueTime,LastAttempt,ConsecutiveFailures"
        return self._get_powershell().run_json(cmd)

    def list_domain_controllers(self, domain=None):
        """Enumerate DC inventory + roles and placement using Get-ADDomainController."""
        params = {"Filter": "*"}
        if domain:
            params["Server"] = domain
        cmd = "Get-ADDomainController" + _ps_params(params)
        cmd += " | Select-Object HostName,Site,IPv4Address,IsGlobalCatalog,IsReadOnly,OperatingSystem,OperatingSystemVersion,OperationMasterRoles,Enabled"
        result = self._get_powershell().run_json(cmd)
        if is_powershell_envelope(result):
            if result.get("ok", True):
                normalized = self._normalize_dc_inventory(unwrap_powershell_data(result))
                return {**result, "data": normalized}
            if domain:
                fallback_result = self._get_powershell().run(f"nltest /dclist:{_ps_quote(domain)}")
                if is_powershell_envelope(fallback_result):
                    raw = unwrap_powershell_data(fallback_result)
                    normalized = self._parse_nltest_dclist(raw)
                    meta = dict(result.get("meta") or {})
                    meta["fallback"] = "nltest"
                    meta["ad_error"] = result.get("error")
                    return {**fallback_result, "ok": True, "data": normalized, "error": None, "meta": meta}
                return fallback_result
            return result
        return self._normalize_dc_inventory(result)

    def get_forest_facts(self):
        """Collect forest facts (domains, GC list, schema/domain naming masters)."""
        cmd = "Get-ADForest | Select-Object Name,RootDomain,ForestMode,Domains,GlobalCatalogs,Sites,SchemaMaster,DomainNamingMaster"
        return self._get_powershell().run_json(cmd)

    def get_domain_facts(self):
        """Collect current domain facts (mode + FSMO role holders)."""
        cmd = "Get-ADDomain | Select-Object DNSRoot,NetBIOSName,DomainMode,PDCEmulator,RIDMaster,InfrastructureMaster"
        return self._get_powershell().run_json(cmd)

    def list_fsmo_role_holders(self):
        """Map each FSMO role to the current role holder."""
        cmd = (
            "Get-ADForest | Select-Object SchemaMaster,DomainNamingMaster;"
            "Get-ADDomain | Select-Object PDCEmulator,RIDMaster,InfrastructureMaster"
        )
        result = self._get_powershell().run_json(cmd)
        if is_powershell_envelope(result) and result.get("ok", True):
            data = unwrap_powershell_data(result)
            forest = data[0] if isinstance(data, list) and data else (data or {})
            domain = data[1] if isinstance(data, list) and len(data) > 1 else {}
            roles = {
                "Schema master": forest.get("SchemaMaster"),
                "Domain naming master": forest.get("DomainNamingMaster"),
                "PDC": domain.get("PDCEmulator"),
                "RID pool manager": domain.get("RIDMaster"),
                "Infrastructure master": domain.get("InfrastructureMaster"),
            }
            return {**result, "data": {"roles": roles}}

        # Fallback to netdom if AD cmdlets are unavailable or failed.
        netdom_result = self._get_powershell().run("netdom query fsmo")
        return _wrap_envelope(
            netdom_result,
            lambda output: {
                "roles": self._parse_fsmo_output(output or ""),
                "raw_text": output,
            },
        )

    def get_sysvol_migration_state(self):
        """Check SYSVOL DFSR migration state (important for legacy domains)."""
        result = self._get_powershell().run("dfsrmig /getglobalstate")
        return _wrap_envelope(result, lambda output: {"raw_text": output})

    def get_time_sync_status(self):
        """Get local Windows time service state (Kerberos health dependency)."""
        result = self._get_powershell().run("w32tm /query /status")
        return _wrap_envelope(result, lambda output: {"raw_text": output})

    def monitor_time_sync(self, domain=None):
        """Monitor time source/skew across domain members using w32tm /monitor."""
        cmd = "w32tm /monitor"
        if domain:
            cmd += f" /domain:{_ps_quote(domain)}"
        result = self._get_powershell().run(cmd)
        return _wrap_envelope(result, lambda output: {"domain": domain, "raw_text": output})

    def get_time_sync_health(self, domain=None):
        """Run w32tm status + monitor to flag skew risk and time source anomalies."""
        status_env = self._get_powershell().run("w32tm /query /status")
        monitor_cmd = "w32tm /monitor"
        if domain:
            monitor_cmd += f" /domain:{_ps_quote(domain)}"
        monitor_env = self._get_powershell().run(monitor_cmd)

        status_ok = not is_powershell_envelope(status_env) or status_env.get("ok", True)
        monitor_ok = not is_powershell_envelope(monitor_env) or monitor_env.get("ok", True)

        status_raw = unwrap_powershell_data(status_env) if is_powershell_envelope(status_env) else status_env
        monitor_raw = unwrap_powershell_data(monitor_env) if is_powershell_envelope(monitor_env) else monitor_env

        status_parsed = self._parse_w32tm_status(status_raw)
        monitor_parsed = self._parse_w32tm_monitor(monitor_raw)
        flags = self._evaluate_time_sync_flags(status_parsed, monitor_parsed)

        errors = []
        if is_powershell_envelope(status_env) and not status_env.get("ok", True):
            errors.append({"stage": "status", "error": status_env.get("error")})
        if is_powershell_envelope(monitor_env) and not monitor_env.get("ok", True):
            errors.append({"stage": "monitor", "error": monitor_env.get("error")})

        ok = len(errors) == 0
        meta = {
            "domain": domain,
            "status_meta": status_env.get("meta") if isinstance(status_env, dict) else None,
            "monitor_meta": monitor_env.get("meta") if isinstance(monitor_env, dict) else None,
        }
        return {
            "ok": ok,
            "data": {
                "status": status_parsed,
                "monitor": monitor_parsed,
                "flags": flags,
            },
            "error": None if ok else {"message": "Time sync check failed.", "details": errors},
            "meta": meta,
        }

    # Backwards-compatible aliases.
    def replication_summary(self):
        return self.get_replication_health_summary()

    def show_replication(self, dc):
        return self.get_replication_partners_for_dc(dc)

    def replication_queue(self, dc):
        return self.get_replication_queue_for_dc(dc)

    def replication_sync_all(self, dc, flags="AdeP"):
        return self.force_replication_sync_all(dc, flags=flags, execute=True)

    def dc_health_check(self):
        return self.run_dc_health_checks(verbose=True)

    def nltest_list_dcs(self, domain):
        return self.list_domain_controllers_via_nltest(domain)

    def nltest_get_dc(self, domain):
        return self.get_current_dc_for_domain(domain)

    def replication_partner_metadata(self, dc=None):
        return self.get_replication_partner_metadata(dc=dc)

    def replication_failures(self, dc=None):
        return self.get_replication_failures(dc=dc)

    def replication_queue_ops(self, dc=None):
        return self.get_replication_queue_operations(dc=dc)

    def get_forest_info(self):
        return self.get_forest_facts()

    def get_domain_info(self):
        return self.get_domain_facts()

    def query_fsmo_roles(self):
        return self.list_fsmo_role_holders()

    def sysvol_migration_state(self):
        return self.get_sysvol_migration_state()

    def time_status(self):
        return self.get_time_sync_status()

    def time_monitor(self, domain=None):
        return self.monitor_time_sync(domain=domain)


class LocalDomainControllerPowerShellClient(PowerShellModuleClient):
    def __init__(self, session=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        return self.connect_script

    def _disconnect_script(self):
        return self.disconnect_script
