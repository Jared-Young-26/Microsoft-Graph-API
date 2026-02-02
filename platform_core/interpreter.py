from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

SCHEMA_VERSION = 1

ENTITY_OVERRIDES = {
    ("entra", "list_users"): "user",
    ("entra", "create_user"): "user",
    ("entra", "update_user"): "user",
    ("entra", "list_groups"): "group",
    ("entra", "list_group_members"): "user",
    ("entra", "list_service_principals"): "service_principal",
    ("entra", "list_applications"): "application",
    ("exchange", "list_mail_folders"): "mail_folder",
    ("exchange", "list_messages"): "message",
    ("exchange", "list_events"): "event",
    ("exchange", "list_mailbox_permissions"): "mailbox_permission",
    ("exchange", "list_send_as_permissions"): "mailbox_permission",
    ("exchange", "list_send_on_behalf"): "mailbox_permission",
    ("exchange", "list_mailbox_folder_permissions"): "mailbox_folder_permission",
    ("onedrive", "list_drive_items"): "drive_item",
    ("onedrive", "get_user_drive_id"): "drive",
    ("sharepoint", "list_sites"): "site",
    ("sharepoint", "list_sites_admin"): "site",
    ("sharepoint", "list_list_items"): "list_item",
    ("sharepoint", "list_list_columns"): "list_column",
    ("sharepoint", "list_site_permissions"): "site_permission",
    ("teams", "list_joined_teams"): "team",
    ("teams", "list_channels"): "channel",
    ("teams", "list_chat_messages"): "message",
    ("localad", "list_users"): "user",
    ("localad", "list_groups"): "group",
    ("localad", "list_ous"): "ou",
    ("localad", "list_gpos"): "gpo",
    ("printers", "list_printers"): "printer",
    ("printers", "list_gpo_printer_mappings"): "printer_gpo_mapping",
    ("network", "list_adapters"): "network_adapter",
    ("topology", "collect_topology"): "topology_snapshot",
}

PLURAL_ALIASES = {
    "users": "user",
    "groups": "group",
    "sites": "site",
    "messages": "message",
    "events": "event",
    "folders": "mail_folder",
    "drives": "drive",
    "drive_items": "drive_item",
    "teams_admin": "team",
    "teams": "team",
    "channels": "channel",
    "permissions": "permission",
    "gpos": "gpo",
    "ous": "ou",
    "printers": "printer",
    "adapters": "network_adapter",
}

LIST_KEYS = (
    "value",
    "items",
    "results",
    "Result",
    "Results",
    "rows",
    "Rows",
    "printers",
    "Printers",
    "matches",
    "Matches",
)

COMMON_ID_KEYS = (
    "id",
    "Id",
    "ID",
    "objectId",
    "ObjectId",
    "ObjectID",
    "guid",
    "Guid",
    "GUID",
    "objectGuid",
    "ObjectGUID",
    "ObjectGuid",
)

COMMON_NAME_KEYS = (
    "displayName",
    "DisplayName",
    "name",
    "Name",
    "subject",
    "Subject",
    "title",
    "Title",
)

ENTITY_FIELDS = {
    "user": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS + ("fullName", "FullName"),
        "user_principal_name": ("userPrincipalName", "UserPrincipalName", "UPN", "User", "UserId"),
        "mail": ("mail", "Mail", "email", "Email", "EmailAddress", "PrimarySmtpAddress"),
        "sam_account_name": ("samAccountName", "SamAccountName", "SAMAccountName"),
        "distinguished_name": ("distinguishedName", "DistinguishedName"),
        "account_enabled": ("accountEnabled", "AccountEnabled", "Enabled"),
        "department": ("department", "Department"),
        "job_title": ("jobTitle", "JobTitle", "Title"),
        "office_location": ("officeLocation", "OfficeLocation"),
    },
    "group": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS,
        "mail": ("mail", "Mail", "EmailAddress"),
        "mail_nickname": ("mailNickname", "MailNickname"),
        "description": ("description", "Description"),
        "security_enabled": ("securityEnabled", "SecurityEnabled"),
        "group_types": ("groupTypes", "GroupTypes"),
        "visibility": ("visibility", "Visibility"),
    },
    "site": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS,
        "web_url": ("webUrl", "WebUrl", "Url", "url"),
        "site_url": ("siteUrl", "SiteUrl"),
        "owner": ("owner", "Owner"),
    },
    "drive_item": {
        "id": COMMON_ID_KEYS,
        "display_name": ("name", "Name"),
        "web_url": ("webUrl", "WebUrl", "Url", "url"),
        "item_type": ("folder", "file", "package", "ItemType"),
    },
    "drive": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS + ("name", "Name"),
        "owner": ("owner", "Owner"),
        "drive_type": ("driveType", "DriveType"),
    },
    "team": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS,
        "description": ("description", "Description"),
        "visibility": ("visibility", "Visibility"),
    },
    "channel": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS,
        "description": ("description", "Description"),
        "membership_type": ("membershipType", "MembershipType"),
    },
    "message": {
        "id": COMMON_ID_KEYS,
        "display_name": ("subject", "Subject"),
        "from": ("from", "From"),
        "received": ("receivedDateTime", "ReceivedDateTime"),
        "sent": ("sentDateTime", "SentDateTime"),
    },
    "event": {
        "id": COMMON_ID_KEYS,
        "display_name": ("subject", "Subject"),
        "start": ("start", "Start"),
        "end": ("end", "End"),
        "organizer": ("organizer", "Organizer"),
    },
    "mail_folder": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS,
        "parent_id": ("parentFolderId", "ParentFolderId"),
        "child_count": ("childFolderCount", "ChildFolderCount"),
    },
    "mailbox_permission": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS,
        "user": ("user", "User", "UserPrincipalName", "UserId"),
        "access_rights": ("accessRights", "AccessRights"),
    },
    "mailbox_folder_permission": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS,
        "user": ("user", "User", "UserPrincipalName", "UserId"),
        "access_rights": ("accessRights", "AccessRights"),
    },
    "printer": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS + ("shareName", "ShareName"),
        "server": ("ServerName", "serverName", "Server"),
        "location": ("Location", "location"),
        "status": ("Status", "PrinterStatus", "status"),
        "share_name": ("ShareName", "shareName"),
    },
    "gpo": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS + ("gpoName", "GpoName"),
        "owner": ("Owner", "owner"),
        "domain": ("DomainName", "domainName"),
        "path": ("Path", "path"),
    },
    "ou": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS,
        "distinguished_name": ("distinguishedName", "DistinguishedName"),
    },
    "service_principal": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS,
        "app_id": ("appId", "AppId"),
        "publisher": ("publisherName", "PublisherName"),
    },
    "application": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS,
        "app_id": ("appId", "AppId"),
        "publisher": ("publisherDomain", "PublisherDomain"),
    },
    "list_item": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS,
        "web_url": ("webUrl", "WebUrl"),
    },
    "list_column": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS,
        "column_type": ("type", "Type"),
        "required": ("required", "Required"),
        "hidden": ("hidden", "Hidden"),
    },
    "site_permission": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS,
        "roles": ("roles", "Roles"),
        "granted_to": ("grantedToIdentities", "GrantedToIdentities", "grantedTo", "GrantedTo"),
    },
    "network_adapter": {
        "id": COMMON_ID_KEYS,
        "display_name": COMMON_NAME_KEYS + ("Name",),
        "status": ("Status", "status"),
        "mac_address": ("MacAddress", "macAddress"),
        "if_index": ("InterfaceIndex", "ifIndex"),
    },
}


def _get_value(record: Dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if key in record:
            return record.get(key)
    lowered = {str(k).lower(): k for k in record.keys()}
    for key in keys:
        lookup = str(key).lower()
        if lookup in lowered:
            return record.get(lowered[lookup])
    return None


def _guess_entity(service: str, action: str) -> Optional[str]:
    override = ENTITY_OVERRIDES.get((service, action))
    if override:
        return override
    prefixes = ("list_", "get_", "create_", "update_", "delete_", "add_", "remove_", "set_")
    for prefix in prefixes:
        if action.startswith(prefix):
            token = action[len(prefix):]
            token = PLURAL_ALIASES.get(token, token)
            return token
    return None


def _extract_items(payload: Any) -> List[Any]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in LIST_KEYS:
            value = payload.get(key)
            if isinstance(value, list):
                return value
        return [payload]
    return [payload]


def _coerce_record(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {"value": value}


def _normalize_record(
    entity: str,
    record: Dict[str, Any],
    source: str,
    service: str,
    action: str,
    include_raw: bool,
) -> Dict[str, Any]:
    fields = ENTITY_FIELDS.get(entity, {})
    id_value = _get_value(record, fields.get("id", COMMON_ID_KEYS))
    name_value = _get_value(record, fields.get("display_name", COMMON_NAME_KEYS))
    upn_value = _get_value(record, fields.get("user_principal_name", ()))
    mail_value = _get_value(record, fields.get("mail", ()))
    sam_value = _get_value(record, fields.get("sam_account_name", ()))

    normalized = {
        "entity": entity,
        "source": source,
        "service": service,
        "action": action,
        "id": id_value,
        "name": name_value,
        "user_principal_name": upn_value,
        "mail": mail_value,
        "sam_account_name": sam_value,
    }

    attributes = {}
    for key, keys in fields.items():
        if key in ("id", "display_name", "user_principal_name", "mail", "sam_account_name"):
            continue
        value = _get_value(record, keys)
        if value is not None:
            attributes[key] = value
    if attributes:
        normalized["attributes"] = attributes

    identifiers = []
    for value in (id_value, upn_value, mail_value, sam_value, name_value):
        if value is None:
            continue
        identifiers.append(str(value).lower())
    if identifiers:
        normalized["identifiers"] = sorted(set(identifiers))

    if include_raw:
        normalized["raw"] = record

    return normalized


def interpret_response(
    service: str,
    action: str,
    payload: Any,
    *,
    source: str = "graph",
    include_raw: bool = False,
) -> Dict[str, Any]:
    entity = _guess_entity(service, action) or "record"
    items = []
    for entry in _extract_items(payload):
        record = _coerce_record(entry)
        items.append(_normalize_record(entity, record, source, service, action, include_raw))

    index = {
        "id": {},
        "upn": {},
        "mail": {},
        "sam": {},
        "name": {},
    }
    for idx, item in enumerate(items):
        for key, target in (
            ("id", "id"),
            ("user_principal_name", "upn"),
            ("mail", "mail"),
            ("sam_account_name", "sam"),
            ("name", "name"),
        ):
            value = item.get(key)
            if value is None:
                continue
            handle = str(value).lower()
            bucket = index[target].setdefault(handle, [])
            bucket.append(idx)

    return {
        "schema_version": SCHEMA_VERSION,
        "service": service,
        "action": action,
        "source": source,
        "entity": entity,
        "count": len(items),
        "items": items,
        "index": index,
    }
