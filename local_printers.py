from datetime import datetime, timezone

from microsoft import PowerShellModuleClient


def _ps_quote(value):
    return str(value).replace("'", "''")


class LocalPrinterClient:
    def __init__(self, powershell=None, powershell_options=None):
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = LocalPrinterPowerShellClient(**options)
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

    def list_printers(self, name=None, include_configuration=False):
        name_filter = _ps_quote(name or "")
        include_flag = "$true" if include_configuration else "$false"
        script = f"""
        $filter = '{name_filter}'
        $printers = Get-Printer
        if ($filter -ne '') {{
          $printers = $printers | Where-Object {{ $_.Name -like "*$filter*" -or $_.ShareName -like "*$filter*" }}
        }}
        $results = @()
        foreach ($p in $printers) {{
          $config = $null
          if ({include_flag}) {{
            try {{ $config = Get-PrintConfiguration -PrinterName $p.Name }} catch {{ $config = $null }}
          }}
          $results += [PSCustomObject]@{{
            Name = $p.Name
            ShareName = $p.ShareName
            PortName = $p.PortName
            DriverName = $p.DriverName
            PrinterStatus = $p.PrinterStatus
            Shared = $p.Shared
            Published = $p.Published
            Location = $p.Location
            Comment = $p.Comment
            Configuration = $config
          }}
        }}
        $results
        """
        return self._get_powershell().run_json(script)

    def list_gpo_printer_mappings(self, name=None, include_empty=False):
        name_filter = _ps_quote(name or "")
        include_flag = "$true" if include_empty else "$false"
        script = f"""
        $filter = '{name_filter}'
        $includeEmpty = {include_flag}
        $gpos = Get-GPO -All
        if ($filter -ne '') {{
          $gpos = $gpos | Where-Object {{ $_.DisplayName -like "*$filter*" }}
        }}
        $results = @()
        foreach ($gpo in $gpos) {{
          $uncs = @()
          try {{
            $xml = Get-GPOReport -Guid $gpo.Id -ReportType Xml
            if ($xml) {{
              $matches = [regex]::Matches($xml, "\\\\\\\\[^\\\\\\s\\\"']+\\\\[^\\\\\\s\\\"']+")
              foreach ($m in $matches) {{
                $uncs += $m.Value
              }}
            }}
          }} catch {{}}
          $uncs = $uncs | Sort-Object -Unique
          if ($includeEmpty -or $uncs.Count -gt 0) {{
            $results += [PSCustomObject]@{{
              GpoName = $gpo.DisplayName
              GpoId = $gpo.Id.ToString()
              UncPaths = $uncs
            }}
          }}
        }}
        $results
        """
        return self._get_powershell().run_json(script)

    def cross_reference_printers_gpo(self, name=None, include_unmapped=True):
        printers = self.list_printers(name=name, include_configuration=False)
        gpo_mappings = self.list_gpo_printer_mappings()

        def _ensure_list(value):
            if value is None:
                return []
            if isinstance(value, list):
                return value
            return [value]

        printers_list = _ensure_list(printers)
        gpo_list = _ensure_list(gpo_mappings)

        by_name = {p.get("Name"): p for p in printers_list if p.get("Name")}
        by_share = {p.get("ShareName"): p for p in printers_list if p.get("ShareName")}

        matches = []
        conflicts = []
        matched_printers = set()
        share_to_gpos = {}

        for gpo in gpo_list:
            gpo_name = gpo.get("GpoName")
            gpo_id = gpo.get("GpoId")
            for path in gpo.get("UncPaths") or []:
                share = path.split("\\")[-1] if path else ""
                if share:
                    share_to_gpos.setdefault(share, []).append(gpo_name)
                match = by_share.get(share) or by_name.get(share)
                if match:
                    matches.append(
                        {
                            "gpo_name": gpo_name,
                            "gpo_id": gpo_id,
                            "printer_name": match.get("Name"),
                            "share_name": match.get("ShareName"),
                            "unc_path": path,
                        }
                    )
                    matched_printers.add(match.get("Name") or share)
                else:
                    conflicts.append(
                        {
                            "type": "gpo_printer_missing",
                            "gpo_name": gpo_name,
                            "gpo_id": gpo_id,
                            "unc_path": path,
                            "message": "Printer referenced in GPO not found on print server.",
                        }
                    )

        for share, gpos in share_to_gpos.items():
            if len(gpos) > 1:
                conflicts.append(
                    {
                        "type": "duplicate_gpo_printer",
                        "share_name": share,
                        "gpos": gpos,
                        "message": "Printer share referenced by multiple GPOs.",
                    }
                )

        if include_unmapped:
            for printer in printers_list:
                name = printer.get("Name")
                if not name or name in matched_printers:
                    continue
                conflicts.append(
                    {
                        "type": "printer_not_in_gpo",
                        "printer_name": name,
                        "share_name": printer.get("ShareName"),
                        "message": "Printer not referenced by any GPO deployment.",
                    }
                )

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "counts": {
                "printers": len(printers_list),
                "gpo_mappings": len(gpo_list),
                "matches": len(matches),
                "conflicts": len(conflicts),
            },
            "printers": printers_list,
            "gpo_printer_mappings": gpo_list,
            "matches": matches,
            "conflicts": conflicts,
        }


class LocalPrinterPowerShellClient(PowerShellModuleClient):
    def __init__(self, session=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        if self.connect_script:
            return self.connect_script
        return "Import-Module PrintManagement; Import-Module GroupPolicy"

    def _disconnect_script(self):
        return self.disconnect_script
