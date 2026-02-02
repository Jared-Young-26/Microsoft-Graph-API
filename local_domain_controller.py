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
    for key, value in (params or {}).items():
        if value is None:
            continue
        parts.append(f"-{key} {_ps_value(value)}")
    return (" " + " ".join(parts)) if parts else ""


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

    def replication_summary(self):
        return self._get_powershell().run("repadmin /replsummary")

    def show_replication(self, dc):
        cmd = f"repadmin /showrepl {_ps_value(dc)}"
        return self._get_powershell().run(cmd)

    def replication_queue(self, dc):
        cmd = f"repadmin /queue {_ps_value(dc)}"
        return self._get_powershell().run(cmd)

    def replication_sync_all(self, dc, flags="AdeP"):
        flags = str(flags or "").lstrip("/")
        cmd = f"repadmin /syncall {_ps_value(dc)}"
        if flags:
            cmd += f" /{flags}"
        return self._get_powershell().run(cmd)

    def dc_health_check(self):
        return self._get_powershell().run("dcdiag /v")

    def nltest_list_dcs(self, domain):
        cmd = f"nltest /dclist:{_ps_quote(domain)}"
        return self._get_powershell().run(cmd)

    def nltest_get_dc(self, domain):
        cmd = f"nltest /dsgetdc:{_ps_quote(domain)}"
        return self._get_powershell().run(cmd)

    def replication_partner_metadata(self, dc=None):
        params = {"Target": dc} if dc else {}
        cmd = "Get-ADReplicationPartnerMetadata" + _ps_params(params)
        cmd += " | Select-Object Server,Partner,PartnerType,LastReplicationSuccess,LastReplicationAttempt,LastReplicationResult,ConsecutiveReplicationFailures"
        return self._get_powershell().run_json(cmd)

    def replication_failures(self, dc=None):
        params = {"Target": dc} if dc else {}
        cmd = "Get-ADReplicationFailure" + _ps_params(params)
        cmd += " | Select-Object Server,Partner,FirstFailureTime,FailureCount,LastError"
        return self._get_powershell().run_json(cmd)

    def replication_queue_ops(self, dc=None):
        params = {"Server": dc} if dc else {}
        cmd = "Get-ADReplicationQueueOperation" + _ps_params(params)
        cmd += " | Select-Object Server,OperationType,Partition,QueueTime,LastAttempt,ConsecutiveFailures"
        return self._get_powershell().run_json(cmd)

    def list_domain_controllers(self, domain=None):
        params = {"Filter": "*"}
        if domain:
            params["Server"] = domain
        cmd = "Get-ADDomainController" + _ps_params(params)
        cmd += " | Select-Object HostName,Site,IPv4Address,IsGlobalCatalog,IsReadOnly,OperatingSystem,OperationMasterRoles,Enabled"
        return self._get_powershell().run_json(cmd)

    def get_forest_info(self):
        cmd = "Get-ADForest | Select-Object Name,RootDomain,ForestMode,Domains,GlobalCatalogs,Sites,SchemaMaster,DomainNamingMaster"
        return self._get_powershell().run_json(cmd)

    def get_domain_info(self):
        cmd = "Get-ADDomain | Select-Object DNSRoot,NetBIOSName,DomainMode,PDCEmulator,RIDMaster,InfrastructureMaster"
        return self._get_powershell().run_json(cmd)

    def query_fsmo_roles(self):
        return self._get_powershell().run("netdom query fsmo")

    def sysvol_migration_state(self):
        return self._get_powershell().run("dfsrmig /getglobalstate")

    def time_status(self):
        return self._get_powershell().run("w32tm /query /status")

    def time_monitor(self, domain=None):
        cmd = "w32tm /monitor"
        if domain:
            cmd += f" /domain:{_ps_quote(domain)}"
        return self._get_powershell().run(cmd)


class LocalDomainControllerPowerShellClient(PowerShellModuleClient):
    def __init__(self, session=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        return self.connect_script

    def _disconnect_script(self):
        return self.disconnect_script
