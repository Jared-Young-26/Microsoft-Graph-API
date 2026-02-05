from platform_core.probe_handlers import (
    process_inventory_probe,
    service_process_map_probe,
)
from microsoft import is_powershell_envelope


def _unwrap(result):
    """Internal helper for unwrap."""
    if is_powershell_envelope(result):
        return result.get("data")
    return result


class LocalProcessClient:
    """Client for Local Process operations."""
    def __init__(self, powershell=None, config=None):
        """Initialize the instance."""
        self._powershell = powershell
        self._config = config or {}

    def _context(self):
        """Internal helper for context."""
        return {"powershell": self._powershell}

    def process_inventory(self, include_command_line=None, max_items=None):
        """Run process inventory."""
        if include_command_line is None:
            include_command_line = bool(self._config.get("process_include_command_line", False))
        if max_items is None:
            max_items = int(self._config.get("process_max_items") or 200)
        else:
            try:
                max_items = int(max_items)
            except Exception:
                max_items = int(self._config.get("process_max_items") or 200)
        result = process_inventory_probe(
            None,
            self._context(),
            {"inputs": {"include_command_line": include_command_line, "max_items": max_items}},
        )
        return _unwrap(result)

    def service_process_map(self, max_items=None):
        """Run service process map."""
        if max_items is None:
            max_items = int(self._config.get("process_max_items") or 200)
        else:
            try:
                max_items = int(max_items)
            except Exception:
                max_items = int(self._config.get("process_max_items") or 200)
        result = service_process_map_probe(None, self._context(), {"inputs": {"max_items": max_items}})
        return _unwrap(result)
