from platform_core.probe_handlers import cert_inventory_probe, tls_probe as tls_probe_handler
from microsoft import is_powershell_envelope


def _unwrap(result):
    """Internal helper for unwrap."""
    if is_powershell_envelope(result):
        return result.get("data")
    return result


class LocalCertificateClient:
    """Client for Local Certificate operations."""
    def __init__(self, powershell=None, config=None):
        """Initialize the instance."""
        self._powershell = powershell
        self._config = config or {}

    def _context(self):
        """Internal helper for context."""
        return {"powershell": self._powershell}

    def list_machine_certificates(self, stores=None, expiring_days=None):
        """List machine certificates."""
        if stores is None:
            stores = self._config.get("cert_stores") or ["My", "Root", "CA"]
        if expiring_days is None:
            expiring_days = int(self._config.get("cert_expiring_days") or 30)
        else:
            try:
                expiring_days = int(expiring_days)
            except Exception:
                expiring_days = int(self._config.get("cert_expiring_days") or 30)
        result = cert_inventory_probe(None, self._context(), {"inputs": {"stores": stores, "expiring_days": expiring_days}})
        return _unwrap(result)

    def tls_probe(self, targets=None, port=443):
        """Run tls probe."""
        if targets is None:
            targets = self._config.get("tls_endpoints") or [
                "graph.microsoft.com",
                "login.microsoftonline.com",
            ]
        try:
            port = int(port)
        except Exception:
            port = 443
        result = tls_probe_handler(None, self._context(), {"inputs": {"targets": targets, "port": port}})
        return _unwrap(result)
