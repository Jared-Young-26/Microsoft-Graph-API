from microsoft import ServiceClient, PowerShellModuleClient


def _ps_quote(value):
    return str(value).replace("'", "''")


class ExchangeClient(ServiceClient):
    def __init__(self, graph_session, powershell=None, powershell_options=None):
        super().__init__(graph_session)
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = ExchangePowerShellClient(**options)
        return self._powershell

    def connect_powershell(self, **options):
        return self._get_powershell(**options).connect()

    def disconnect_powershell(self):
        if self._powershell:
            return self._powershell.disconnect()
        return True

    def shared_mailbox_sent_items_commands(self, shared_mailbox):
        return ExchangePowerShellClient.shared_mailbox_sent_items_commands(shared_mailbox)

    def shared_mailbox_sent_items_status_command(self, shared_mailbox):
        return ExchangePowerShellClient.shared_mailbox_sent_items_status_command(shared_mailbox)

    def enable_shared_mailbox_sent_items(self, shared_mailbox, execute=False, **powershell_options):
        commands = self.shared_mailbox_sent_items_commands(shared_mailbox)
        if not execute:
            return "\n".join(commands)
        ps = self._get_powershell(**powershell_options)
        return ps.enable_shared_mailbox_sent_items(shared_mailbox)

    def get_shared_mailbox_sent_items_settings(self, shared_mailbox, execute=False, **powershell_options):
        command = self.shared_mailbox_sent_items_status_command(shared_mailbox)
        if not execute:
            return command
        ps = self._get_powershell(**powershell_options)
        return ps.run(command)

    def list_mailbox_permissions(self, shared_mailbox, **powershell_options):
        ps = self._get_powershell(**powershell_options)
        return ps.list_mailbox_permissions(shared_mailbox)

    def add_mailbox_permission(
        self, shared_mailbox, user_id, access_rights="FullAccess", automapping=True, **powershell_options
    ):
        ps = self._get_powershell(**powershell_options)
        return ps.add_mailbox_permission(shared_mailbox, user_id, access_rights=access_rights, automapping=automapping)

    def remove_mailbox_permission(self, shared_mailbox, user_id, access_rights="FullAccess", **powershell_options):
        ps = self._get_powershell(**powershell_options)
        return ps.remove_mailbox_permission(shared_mailbox, user_id, access_rights=access_rights)

    def list_send_as_permissions(self, shared_mailbox, **powershell_options):
        ps = self._get_powershell(**powershell_options)
        return ps.list_send_as_permissions(shared_mailbox)

    def add_send_as_permission(self, shared_mailbox, user_id, **powershell_options):
        ps = self._get_powershell(**powershell_options)
        return ps.add_send_as_permission(shared_mailbox, user_id)

    def remove_send_as_permission(self, shared_mailbox, user_id, **powershell_options):
        ps = self._get_powershell(**powershell_options)
        return ps.remove_send_as_permission(shared_mailbox, user_id)

    def list_send_on_behalf(self, shared_mailbox, **powershell_options):
        ps = self._get_powershell(**powershell_options)
        return ps.list_send_on_behalf(shared_mailbox)

    def add_send_on_behalf(self, shared_mailbox, user_id, **powershell_options):
        ps = self._get_powershell(**powershell_options)
        return ps.add_send_on_behalf(shared_mailbox, user_id)

    def remove_send_on_behalf(self, shared_mailbox, user_id, **powershell_options):
        ps = self._get_powershell(**powershell_options)
        return ps.remove_send_on_behalf(shared_mailbox, user_id)

    def list_mailbox_folder_permissions(self, shared_mailbox, folder_path="Calendar", **powershell_options):
        ps = self._get_powershell(**powershell_options)
        return ps.list_mailbox_folder_permissions(shared_mailbox, folder_path)

    def add_mailbox_folder_permission(
        self,
        shared_mailbox,
        folder_path,
        user_id,
        access_rights="Editor",
        delegate=False,
        **powershell_options,
    ):
        ps = self._get_powershell(**powershell_options)
        return ps.add_mailbox_folder_permission(
            shared_mailbox,
            folder_path,
            user_id,
            access_rights=access_rights,
            delegate=delegate,
        )

    def update_mailbox_folder_permission(
        self,
        shared_mailbox,
        folder_path,
        user_id,
        access_rights="Editor",
        delegate=False,
        **powershell_options,
    ):
        ps = self._get_powershell(**powershell_options)
        return ps.update_mailbox_folder_permission(
            shared_mailbox,
            folder_path,
            user_id,
            access_rights=access_rights,
            delegate=delegate,
        )

    def remove_mailbox_folder_permission(self, shared_mailbox, folder_path, user_id, **powershell_options):
        ps = self._get_powershell(**powershell_options)
        return ps.remove_mailbox_folder_permission(shared_mailbox, folder_path, user_id)

    def list_mail_folders(self, user_id="me", include_hidden=False, top=100):
        params = {"$top": top}
        if include_hidden:
            params["includeHiddenFolders"] = "true"
        url = f"/users/{user_id}/mailFolders" if user_id != "me" else "/me/mailFolders"
        response = self.get(url, params=params)
        return response.json().get("value", [])

    def get_mail_folder(self, folder_id, user_id="me"):
        url = f"/users/{user_id}/mailFolders/{folder_id}" if user_id != "me" else f"/me/mailFolders/{folder_id}"
        response = self.get(url)
        return response.json()

    def create_mail_folder(self, display_name, parent_folder_id=None, user_id="me"):
        if parent_folder_id:
            url = f"/users/{user_id}/mailFolders/{parent_folder_id}/childFolders" if user_id != "me" else f"/me/mailFolders/{parent_folder_id}/childFolders"
        else:
            url = f"/users/{user_id}/mailFolders" if user_id != "me" else "/me/mailFolders"
        payload = {"displayName": display_name}
        response = self.post(url, json=payload)
        return response.json()

    def list_messages(self, user_id="me", top=10, select=None, order_by="receivedDateTime desc"):
        params = {"$top": top, "$orderBy": order_by}
        if select:
            params["$select"] = ",".join(select) if isinstance(select, (list, tuple)) else select
        url = f"/users/{user_id}/messages" if user_id != "me" else "/me/messages"
        response = self.get(url, params=params)
        return response.json().get("value", [])

    def list_messages_in_folder(self, folder_id, user_id="me", top=25, select=None, order_by="receivedDateTime desc", filter_query=None, search=None):
        params = {"$top": top, "$orderBy": order_by}
        headers = None
        if select:
            params["$select"] = ",".join(select) if isinstance(select, (list, tuple)) else select
        if filter_query:
            params["$filter"] = filter_query
        if search:
            params["$search"] = f"\"{search}\""
            headers = {"ConsistencyLevel": "eventual"}

        url = f"/users/{user_id}/mailFolders/{folder_id}/messages" if user_id != "me" else f"/me/mailFolders/{folder_id}/messages"
        response = self.get(url, params=params, headers=headers) if headers else self.get(url, params=params)
        return response.json().get("value", [])

    def get_message(self, message_id, user_id="me"):
        url = f"/users/{user_id}/messages/{message_id}" if user_id != "me" else f"/me/messages/{message_id}"
        response = self.get(url)
        return response.json()

    def move_message(self, message_id, destination_folder_id, user_id="me"):
        url = f"/users/{user_id}/messages/{message_id}/move" if user_id != "me" else f"/me/messages/{message_id}/move"
        payload = {"destinationId": destination_folder_id}
        response = self.post(url, json=payload)
        return response.json()

    def copy_message(self, message_id, destination_folder_id, user_id="me"):
        url = f"/users/{user_id}/messages/{message_id}/copy" if user_id != "me" else f"/me/messages/{message_id}/copy"
        payload = {"destinationId": destination_folder_id}
        response = self.post(url, json=payload)
        return response.json()

    def delete_message(self, message_id, user_id="me"):
        url = f"/users/{user_id}/messages/{message_id}" if user_id != "me" else f"/me/messages/{message_id}"
        self.delete(url)
        return True

    def list_message_attachments(self, message_id, user_id="me"):
        url = f"/users/{user_id}/messages/{message_id}/attachments" if user_id != "me" else f"/me/messages/{message_id}/attachments"
        response = self.get(url)
        return response.json().get("value", [])

    def get_attachment(self, message_id, attachment_id, user_id="me"):
        url = f"/users/{user_id}/messages/{message_id}/attachments/{attachment_id}" if user_id != "me" else f"/me/messages/{message_id}/attachments/{attachment_id}"
        response = self.get(url)
        return response.json()

    def send_mail(self, subject, body, to_recipients, cc_recipients=None, bcc_recipients=None, user_id="me"):
        def _format_recipients(recipients):
            return [{"emailAddress": {"address": r}} for r in recipients]

        message = {
            "subject": subject,
            "body": {"contentType": "HTML", "content": body},
            "toRecipients": _format_recipients(to_recipients),
        }
        if cc_recipients:
            message["ccRecipients"] = _format_recipients(cc_recipients)
        if bcc_recipients:
            message["bccRecipients"] = _format_recipients(bcc_recipients)

        url = f"/users/{user_id}/sendMail" if user_id != "me" else "/me/sendMail"
        payload = {"message": message, "saveToSentItems": True}
        self.post(url, json=payload)
        return True

    def send_mail_from_shared_mailbox(
        self,
        shared_mailbox,
        subject,
        body,
        to_recipients,
        cc_recipients=None,
        bcc_recipients=None,
        reply_to=None,
    ):
        def _format_recipients(recipients):
            return [{"emailAddress": {"address": r}} for r in recipients]

        message = {
            "subject": subject,
            "body": {"contentType": "HTML", "content": body},
            "toRecipients": _format_recipients(to_recipients),
            "from": {"emailAddress": {"address": shared_mailbox}},
            "sender": {"emailAddress": {"address": shared_mailbox}},
        }
        if cc_recipients:
            message["ccRecipients"] = _format_recipients(cc_recipients)
        if bcc_recipients:
            message["bccRecipients"] = _format_recipients(bcc_recipients)
        if reply_to:
            message["replyTo"] = _format_recipients(reply_to if isinstance(reply_to, (list, tuple)) else [reply_to])

        # Create the draft in the shared mailbox so it saves to the shared Sent Items.
        draft_response = self.post(f"/users/{shared_mailbox}/messages", json=message)
        draft = draft_response.json()
        message_id = draft.get("id")

        if not message_id:
            raise RuntimeError("Failed to create shared mailbox draft message.")

        self.post(f"/users/{shared_mailbox}/messages/{message_id}/send")
        return True

    def list_calendars(self, user_id="me"):
        url = f"/users/{user_id}/calendars" if user_id != "me" else "/me/calendars"
        response = self.get(url)
        return response.json().get("value", [])

    def get_calendar(self, calendar_id, user_id="me"):
        url = f"/users/{user_id}/calendars/{calendar_id}" if user_id != "me" else f"/me/calendars/{calendar_id}"
        response = self.get(url)
        return response.json()

    def create_calendar(self, name, color=None, user_id="me"):
        payload = {"name": name}
        if color:
            payload["color"] = color
        url = f"/users/{user_id}/calendars" if user_id != "me" else "/me/calendars"
        response = self.post(url, json=payload)
        return response.json()

    def update_calendar(self, calendar_id, updates, user_id="me"):
        url = f"/users/{user_id}/calendars/{calendar_id}" if user_id != "me" else f"/me/calendars/{calendar_id}"
        response = self.patch(url, json=updates)
        return response.json()

    def delete_calendar(self, calendar_id, user_id="me"):
        url = f"/users/{user_id}/calendars/{calendar_id}" if user_id != "me" else f"/me/calendars/{calendar_id}"
        self.delete(url)
        return True

    def list_events(self, user_id="me", start_iso=None, end_iso=None, top=25, select=None, order_by=None):
        params = {"$top": top}
        if select:
            params["$select"] = ",".join(select) if isinstance(select, (list, tuple)) else select
        if order_by:
            params["$orderBy"] = order_by

        if start_iso and end_iso:
            params["startDateTime"] = start_iso
            params["endDateTime"] = end_iso
            url = f"/users/{user_id}/calendarView" if user_id != "me" else "/me/calendarView"
        else:
            url = f"/users/{user_id}/events" if user_id != "me" else "/me/events"
        response = self.get(url, params=params)
        return response.json().get("value", [])

    def list_calendar_events(self, calendar_id, user_id="me", start_iso=None, end_iso=None, top=25, select=None, order_by=None):
        params = {"$top": top}
        if select:
            params["$select"] = ",".join(select) if isinstance(select, (list, tuple)) else select
        if order_by:
            params["$orderBy"] = order_by

        if start_iso and end_iso:
            params["startDateTime"] = start_iso
            params["endDateTime"] = end_iso
            url = f"/users/{user_id}/calendars/{calendar_id}/calendarView" if user_id != "me" else f"/me/calendars/{calendar_id}/calendarView"
        else:
            url = f"/users/{user_id}/calendars/{calendar_id}/events" if user_id != "me" else f"/me/calendars/{calendar_id}/events"
        response = self.get(url, params=params)
        return response.json().get("value", [])

    def create_calendar_event(self, subject, start_iso, end_iso, time_zone="UTC", attendees=None, user_id="me"):
        event = {
            "subject": subject,
            "start": {"dateTime": start_iso, "timeZone": time_zone},
            "end": {"dateTime": end_iso, "timeZone": time_zone},
        }
        if attendees:
            event["attendees"] = [{"emailAddress": {"address": a}, "type": "required"} for a in attendees]

        url = f"/users/{user_id}/events" if user_id != "me" else "/me/events"
        response = self.post(url, json=event)
        return response.json()

    def get_event(self, event_id, user_id="me"):
        url = f"/users/{user_id}/events/{event_id}" if user_id != "me" else f"/me/events/{event_id}"
        response = self.get(url)
        return response.json()

    def get_event_instances(self, event_id, start_iso, end_iso, user_id="me"):
        params = {"startDateTime": start_iso, "endDateTime": end_iso}
        url = f"/users/{user_id}/events/{event_id}/instances" if user_id != "me" else f"/me/events/{event_id}/instances"
        response = self.get(url, params=params)
        return response.json().get("value", [])

    def update_event(self, event_id, updates, user_id="me"):
        url = f"/users/{user_id}/events/{event_id}" if user_id != "me" else f"/me/events/{event_id}"
        response = self.patch(url, json=updates)
        return response.json()

    def delete_event(self, event_id, user_id="me"):
        url = f"/users/{user_id}/events/{event_id}" if user_id != "me" else f"/me/events/{event_id}"
        self.delete(url)
        return True

    def cancel_event(self, event_id, comment=None, user_id="me"):
        payload = {"comment": comment} if comment else {}
        url = f"/users/{user_id}/events/{event_id}/cancel" if user_id != "me" else f"/me/events/{event_id}/cancel"
        self.post(url, json=payload)
        return True

    def respond_to_event(self, event_id, response="accept", comment=None, send_response=True, user_id="me"):
        action = {
            "accept": "accept",
            "tentative": "tentativelyAccept",
            "decline": "decline",
        }.get(response)
        if not action:
            raise ValueError("response must be one of: accept, tentative, decline")
        payload = {"sendResponse": send_response}
        if comment:
            payload["comment"] = comment
        url = f"/users/{user_id}/events/{event_id}/{action}" if user_id != "me" else f"/me/events/{event_id}/{action}"
        self.post(url, json=payload)
        return True

    def list_event_attachments(self, event_id, user_id="me"):
        url = f"/users/{user_id}/events/{event_id}/attachments" if user_id != "me" else f"/me/events/{event_id}/attachments"
        response = self.get(url)
        return response.json().get("value", [])

    def add_event_attachment(self, event_id, attachment, user_id="me"):
        url = f"/users/{user_id}/events/{event_id}/attachments" if user_id != "me" else f"/me/events/{event_id}/attachments"
        response = self.post(url, json=attachment)
        return response.json()


class ExchangePowerShellClient(PowerShellModuleClient):
    def __init__(
        self,
        session=None,
        auth_mode="interactive",
        user_principal_name=None,
        organization=None,
        show_banner=False,
        pwsh_path="pwsh",
    ):
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.auth_mode = auth_mode
        self.user_principal_name = user_principal_name
        self.organization = organization
        self.show_banner = show_banner

    @staticmethod
    def shared_mailbox_sent_items_commands(shared_mailbox):
        mailbox = _ps_quote(shared_mailbox)
        return [
            f"Set-Mailbox -Identity '{mailbox}' -MessageCopyForSentAsEnabled $true",
            f"Set-Mailbox -Identity '{mailbox}' -MessageCopyForSendOnBehalfEnabled $true",
        ]

    @staticmethod
    def shared_mailbox_sent_items_status_command(shared_mailbox):
        mailbox = _ps_quote(shared_mailbox)
        return (
            "Get-Mailbox "
            f"-Identity '{mailbox}' "
            "| Select MessageCopyForSentAsEnabled, MessageCopyForSendOnBehalfEnabled"
        )

    def list_mailbox_permissions(self, shared_mailbox):
        mailbox = _ps_quote(shared_mailbox)
        cmd = (
            "Get-MailboxPermission "
            f"-Identity '{mailbox}' "
            "| Select User, AccessRights, Deny, IsInherited"
        )
        return self.run_json(cmd)

    def add_mailbox_permission(self, shared_mailbox, user_id, access_rights="FullAccess", automapping=True):
        mailbox = _ps_quote(shared_mailbox)
        user = _ps_quote(user_id)
        rights = access_rights or "FullAccess"
        auto = "$true" if automapping else "$false"
        cmd = (
            "Add-MailboxPermission "
            f"-Identity '{mailbox}' -User '{user}' -AccessRights {rights} "
            f"-InheritanceType All -AutoMapping:{auto}"
        )
        return self.run(cmd)

    def remove_mailbox_permission(self, shared_mailbox, user_id, access_rights="FullAccess"):
        mailbox = _ps_quote(shared_mailbox)
        user = _ps_quote(user_id)
        rights = access_rights or "FullAccess"
        cmd = (
            "Remove-MailboxPermission "
            f"-Identity '{mailbox}' -User '{user}' -AccessRights {rights} "
            "-InheritanceType All -Confirm:$false"
        )
        return self.run(cmd)

    def list_send_as_permissions(self, shared_mailbox):
        mailbox = _ps_quote(shared_mailbox)
        cmd = (
            "Get-RecipientPermission "
            f"-Identity '{mailbox}' "
            "| Select Trustee, AccessRights, IsInherited"
        )
        return self.run_json(cmd)

    def add_send_as_permission(self, shared_mailbox, user_id):
        mailbox = _ps_quote(shared_mailbox)
        user = _ps_quote(user_id)
        cmd = (
            "Add-RecipientPermission "
            f"-Identity '{mailbox}' -Trustee '{user}' -AccessRights SendAs "
            "-Confirm:$false"
        )
        return self.run(cmd)

    def remove_send_as_permission(self, shared_mailbox, user_id):
        mailbox = _ps_quote(shared_mailbox)
        user = _ps_quote(user_id)
        cmd = (
            "Remove-RecipientPermission "
            f"-Identity '{mailbox}' -Trustee '{user}' -AccessRights SendAs "
            "-Confirm:$false"
        )
        return self.run(cmd)

    def list_send_on_behalf(self, shared_mailbox):
        mailbox = _ps_quote(shared_mailbox)
        cmd = (
            "Get-Mailbox "
            f"-Identity '{mailbox}' "
            "| Select GrantSendOnBehalfTo"
        )
        return self.run_json(cmd)

    def add_send_on_behalf(self, shared_mailbox, user_id):
        mailbox = _ps_quote(shared_mailbox)
        user = _ps_quote(user_id)
        cmd = (
            "Set-Mailbox "
            f"-Identity '{mailbox}' "
            f"-GrantSendOnBehalfTo @{{Add='{user}'}}"
        )
        return self.run(cmd)

    def remove_send_on_behalf(self, shared_mailbox, user_id):
        mailbox = _ps_quote(shared_mailbox)
        user = _ps_quote(user_id)
        cmd = (
            "Set-Mailbox "
            f"-Identity '{mailbox}' "
            f"-GrantSendOnBehalfTo @{{Remove='{user}'}}"
        )
        return self.run(cmd)

    def _folder_identity(self, mailbox, folder_path):
        folder = (folder_path or "Calendar").strip()
        folder = folder.lstrip("\\/")
        return f"{mailbox}:\\{folder}"

    def list_mailbox_folder_permissions(self, shared_mailbox, folder_path="Calendar"):
        identity = _ps_quote(self._folder_identity(shared_mailbox, folder_path))
        cmd = (
            "Get-MailboxFolderPermission "
            f"-Identity '{identity}' "
            "| Select User, AccessRights, SharingPermissionFlags, IsInherited"
        )
        return self.run_json(cmd)

    def add_mailbox_folder_permission(
        self, shared_mailbox, folder_path, user_id, access_rights="Editor", delegate=False
    ):
        identity = _ps_quote(self._folder_identity(shared_mailbox, folder_path))
        user = _ps_quote(user_id)
        rights = access_rights or "Editor"
        cmd = (
            "Add-MailboxFolderPermission "
            f"-Identity '{identity}' -User '{user}' -AccessRights {rights}"
        )
        if delegate:
            cmd += " -SharingPermissionFlags Delegate"
        return self.run(cmd)

    def update_mailbox_folder_permission(
        self, shared_mailbox, folder_path, user_id, access_rights="Editor", delegate=False
    ):
        identity = _ps_quote(self._folder_identity(shared_mailbox, folder_path))
        user = _ps_quote(user_id)
        rights = access_rights or "Editor"
        cmd = (
            "Set-MailboxFolderPermission "
            f"-Identity '{identity}' -User '{user}' -AccessRights {rights}"
        )
        if delegate:
            cmd += " -SharingPermissionFlags Delegate"
        return self.run(cmd)

    def remove_mailbox_folder_permission(self, shared_mailbox, folder_path, user_id):
        identity = _ps_quote(self._folder_identity(shared_mailbox, folder_path))
        user = _ps_quote(user_id)
        cmd = (
            "Remove-MailboxFolderPermission "
            f"-Identity '{identity}' -User '{user}' -Confirm:$false"
        )
        return self.run(cmd)

    def _connect_script(self):
        parts = ["Import-Module ExchangeOnlineManagement"]
        cmd = "Connect-ExchangeOnline"
        if self.auth_mode == "device":
            cmd += " -Device"
        if self.user_principal_name:
            cmd += f" -UserPrincipalName '{_ps_quote(self.user_principal_name)}'"
        if self.organization:
            cmd += f" -Organization '{_ps_quote(self.organization)}'"
        if not self.show_banner:
            cmd += " -ShowBanner:$false"
        parts.append(cmd)
        return ";\n".join(parts)

    def enable_shared_mailbox_sent_items(self, shared_mailbox):
        commands = self.shared_mailbox_sent_items_commands(shared_mailbox)
        script = ";\n".join(commands)
        return self.run(script)

    def _disconnect_script(self):
        return "Disconnect-ExchangeOnline -Confirm:$false"

    def list_contacts(self, user_id="me", top=25, select=None):
        params = {"$top": top}
        if select:
            params["$select"] = ",".join(select) if isinstance(select, (list, tuple)) else select
        url = f"/users/{user_id}/contacts" if user_id != "me" else "/me/contacts"
        response = self.get(url, params=params)
        return response.json().get("value", [])

    def create_contact(self, given_name, surname, email, user_id="me", **extra_fields):
        payload = {
            "givenName": given_name,
            "surname": surname,
            "emailAddresses": [{"address": email}],
        }
        payload.update(extra_fields)
        url = f"/users/{user_id}/contacts" if user_id != "me" else "/me/contacts"
        response = self.post(url, json=payload)
        return response.json()

    def update_contact(self, contact_id, updates, user_id="me"):
        url = f"/users/{user_id}/contacts/{contact_id}" if user_id != "me" else f"/me/contacts/{contact_id}"
        response = self.patch(url, json=updates)
        return response.json()

    def delete_contact(self, contact_id, user_id="me"):
        url = f"/users/{user_id}/contacts/{contact_id}" if user_id != "me" else f"/me/contacts/{contact_id}"
        self.delete(url)
        return True
