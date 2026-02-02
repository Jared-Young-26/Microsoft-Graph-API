DEFAULT_WATCHLISTS = {
    "network.core": {
        "watchlist_id": "network.core",
        "name": "Network core",
        "description": "DNS client, proxy, and interface configuration",
        "paths": [
            "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters",
            "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Dhcp\\Parameters",
            "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Internet Settings",
            "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings",
        ],
    },
    "printing.core": {
        "watchlist_id": "printing.core",
        "name": "Printing core",
        "description": "Spooler and printer connection configuration",
        "paths": [
            "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Print",
            "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Print",
        ],
    },
    "auth.core": {
        "watchlist_id": "auth.core",
        "name": "Authentication core",
        "description": "Winlogon and logon policy settings (safe subset)",
        "paths": [
            "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon",
            "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Lsa",
        ],
    },
    "services.core": {
        "watchlist_id": "services.core",
        "name": "Services core",
        "description": "Service startup configurations",
        "paths": [
            "HKLM:\\SYSTEM\\CurrentControlSet\\Services",
        ],
    },
}
