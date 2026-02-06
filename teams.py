from microsoft import ServiceClient, PowerShellModuleClient
import re


def _ps_quote(value):
    """Internal helper for ps quote."""
    return str(value).replace("'", "''")


def _ps_value(value):
    """Internal helper for ps value."""
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
    """Internal helper for ps params."""
    parts = []
    for key, value in params.items():
        if value is None:
            continue
        parts.append(f"-{key} {_ps_value(value)}")
    return " " + " ".join(parts) if parts else ""


class TeamsClient(ServiceClient):
    """Client for Teams operations."""
    def __init__(self, graph_session, powershell=None, powershell_options=None):
        """Initialize the instance."""
        super().__init__(graph_session)
        self._powershell = powershell
        self._powershell_options = powershell_options or {}

    def _get_powershell(self, **overrides):
        """Get powershell."""
        if self._powershell is None:
            options = {**self._powershell_options, **overrides}
            self._powershell = TeamsPowerShellClient(**options)
        return self._powershell

    def connect_powershell(self, **options):
        """Run connect powershell."""
        return self._get_powershell(**options).connect()

    def disconnect_powershell(self):
        """Run disconnect powershell."""
        if self._powershell:
            return self._powershell.disconnect()
        return True

    def run_powershell(self, script, **options):
        """Run powershell."""
        return self._get_powershell(**options).run(script)

    def run_powershell_json(self, script, **options):
        """Run powershell json."""
        return self._get_powershell(**options).run_json(script)

    def list_joined_teams(self):
        """List joined teams."""
        response = self.get("/me/joinedTeams")
        return response.json().get("value", [])

    def list_teams(self, top=50, select=None):
        """List Teams-enabled Microsoft 365 groups (app-friendly).

        Notes:
        - The Graph `/me/joinedTeams` endpoint is delegated-only and does not work for app-only auth.
        - Listing all Teams is performed by filtering groups with the Teams provisioning option.
        """

        params = {
            "$filter": "resourceProvisioningOptions/Any(x:x eq 'Team')",
            "$top": top,
        }
        if select:
            params["$select"] = select
        response = self.get("/groups", params=params)
        return response.json().get("value", [])

    def _resolve_user_id(self, user_id_or_upn):
        """Resolve a user object id from a UPN or id string."""

        value = str(user_id_or_upn or "").strip()
        if not value:
            raise ValueError("user_id is required.")
        if re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}",
            value,
        ):
            return value
        response = self.get(f"/users/{value}", params={"$select": "id,userPrincipalName"})
        body = response.json() if response is not None else {}
        resolved = body.get("id")
        if not resolved:
            raise ValueError("Unable to resolve user id from identifier.")
        return resolved

    def _resolve_team_member_id(self, team_id, user_id_or_upn):
        """Resolve a Teams membership id for a user within a team."""

        user_id = self._resolve_user_id(user_id_or_upn)
        members = self.list_team_members(team_id)
        for member in members:
            if not isinstance(member, dict):
                continue
            # The membership object typically includes `userId` for AAD members.
            if member.get("userId") == user_id:
                return member.get("id")
            # Fallback: some payloads expose the bound user in OData.
            odata_id = str(member.get("user@odata.bind") or "")
            if user_id and user_id in odata_id:
                return member.get("id")
        raise ValueError("Unable to find membership id for user in team.")

    def get_team(self, team_id):
        """Get team."""
        response = self.get(f"/teams/{team_id}")
        return response.json()

    def list_team_members(self, team_id):
        """List team members."""
        response = self.get(f"/teams/{team_id}/members")
        return response.json().get("value", [])

    def add_team_member(self, team_id, user_id, roles=None):
        """Add team member."""
        payload = {
            "@odata.type": "#microsoft.graph.aadUserConversationMember",
            "roles": roles or [],
            "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{user_id}')",
        }
        response = self.post(f"/teams/{team_id}/members", json=payload)
        return response.json()

    def add_member(self, team_id, user_id, roles=None):
        """Add a member to a Team using a user id or UPN."""

        user_id = self._resolve_user_id(user_id)
        return self.add_team_member(team_id, user_id, roles=roles)

    def remove_team_member(self, team_id, membership_id):
        """Remove team member."""
        self.delete(f"/teams/{team_id}/members/{membership_id}")
        return True

    def remove_member(self, team_id, member_id):
        """Remove a member from a Team using membership id or user id/UPN."""

        value = str(member_id or "").strip()
        if not value:
            raise ValueError("member_id is required.")
        membership_id = value
        # If the identifier looks like an email/UPN, resolve membership id first.
        if "@" in value:
            membership_id = self._resolve_team_member_id(team_id, value)
        self.delete(f"/teams/{team_id}/members/{membership_id}")
        return True

    def list_channels(self, team_id):
        """List channels."""
        response = self.get(f"/teams/{team_id}/channels")
        return response.json().get("value", [])

    def get_channel(self, team_id, channel_id):
        """Get channel."""
        response = self.get(f"/teams/{team_id}/channels/{channel_id}")
        return response.json()

    def create_channel(self, team_id, display_name, description=None, membership_type=None):
        """Create channel."""
        payload = {"displayName": display_name}
        if description:
            payload["description"] = description
        if membership_type:
            payload["membershipType"] = membership_type
        response = self.post(f"/teams/{team_id}/channels", json=payload)
        return response.json()

    def update_channel(self, team_id, channel_id, updates):
        """Update channel."""
        response = self.patch(f"/teams/{team_id}/channels/{channel_id}", json=updates)
        return response.json()

    def delete_channel(self, team_id, channel_id):
        """Delete channel."""
        self.delete(f"/teams/{team_id}/channels/{channel_id}")
        return True

    def list_channel_messages(self, team_id, channel_id, top=20):
        """List channel messages."""
        response = self.get(
            f"/teams/{team_id}/channels/{channel_id}/messages",
            params={"$top": top},
        )
        return response.json().get("value", [])

    def send_channel_message(self, team_id, channel_id, content):
        """Run send channel message."""
        payload = {"body": {"contentType": "html", "content": content}}
        response = self.post(f"/teams/{team_id}/channels/{channel_id}/messages", json=payload)
        return response.json()

    def list_channel_message_replies(self, team_id, channel_id, message_id, top=20):
        """List channel message replies."""
        response = self.get(
            f"/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies",
            params={"$top": top},
        )
        return response.json().get("value", [])

    def reply_to_channel_message(self, team_id, channel_id, message_id, content):
        """Run reply to channel message."""
        payload = {"body": {"contentType": "html", "content": content}}
        response = self.post(
            f"/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies",
            json=payload,
        )
        return response.json()

    def list_chats(self):
        """List chats."""
        response = self.get("/me/chats")
        return response.json().get("value", [])

    def get_chat(self, chat_id):
        """Get chat."""
        response = self.get(f"/chats/{chat_id}")
        return response.json()

    def list_chat_messages(self, chat_id, top=20):
        """List chat messages."""
        response = self.get(f"/chats/{chat_id}/messages", params={"$top": top})
        return response.json().get("value", [])

    def send_chat_message(self, chat_id, content):
        """Run send chat message."""
        payload = {"body": {"contentType": "html", "content": content}}
        response = self.post(f"/chats/{chat_id}/messages", json=payload)
        return response.json()

    def list_teams_powershell(self, **powershell_options):
        """List teams powershell."""
        cmd = "Get-Team"
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_policies_powershell(self, **powershell_options):
        """List Teams messaging/meeting/calling policies (PowerShell-best)."""

        script = r"""
$policies = @()
Get-CsTeamsMessagingPolicy | ForEach-Object {
  $policies += [PSCustomObject]@{
    name = $_.Identity
    type = 'Messaging'
    description = $_.Description
    isGlobal = ($_.Identity -eq 'Global')
  }
}
Get-CsTeamsMeetingPolicy | ForEach-Object {
  $policies += [PSCustomObject]@{
    name = $_.Identity
    type = 'Meeting'
    description = $_.Description
    isGlobal = ($_.Identity -eq 'Global')
  }
}
Get-CsTeamsCallingPolicy | ForEach-Object {
  $policies += [PSCustomObject]@{
    name = $_.Identity
    type = 'Calling'
    description = $_.Description
    isGlobal = ($_.Identity -eq 'Global')
  }
}
$policies
"""
        return self._get_powershell(**powershell_options).run_json(script)

    def get_user_policy_assignments_powershell(self, user_upn, **powershell_options):
        """Get Teams policy assignments for a user (PowerShell-best)."""

        script = r"""
$u = Get-CsOnlineUser -Identity $user_upn
$rows = @()
$rows += [PSCustomObject]@{ policyType = 'Messaging'; policyName = $u.TeamsMessagingPolicy }
$rows += [PSCustomObject]@{ policyType = 'Meeting'; policyName = $u.TeamsMeetingPolicy }
$rows += [PSCustomObject]@{ policyType = 'Calling'; policyName = $u.TeamsCallingPolicy }
$rows
"""
        return self._get_powershell(**powershell_options).run_json(script, parameters={"user_upn": user_upn})

    def assign_user_policy_powershell(self, user_upn, policy_type, policy_name, **powershell_options):
        """Assign a Teams policy to a user (PowerShell-best)."""

        script = r"""
$type = ($policy_type | ForEach-Object { $_.ToString().Trim().ToLowerInvariant() })
switch ($type) {
  'messaging' { Grant-CsTeamsMessagingPolicy -Identity $user_upn -PolicyName $policy_name }
  'meeting' { Grant-CsTeamsMeetingPolicy -Identity $user_upn -PolicyName $policy_name }
  'calling' { Grant-CsTeamsCallingPolicy -Identity $user_upn -PolicyName $policy_name }
  default { throw "Unknown policy_type '$policy_type'. Use messaging|meeting|calling." }
}
Get-CsOnlineUser -Identity $user_upn | Select-Object TeamsMessagingPolicy, TeamsMeetingPolicy, TeamsCallingPolicy
"""
        return self._get_powershell(**powershell_options).run_json(
            script,
            parameters={"user_upn": user_upn, "policy_type": policy_type, "policy_name": policy_name},
        )

    def remove_user_policy_powershell(self, user_upn, policy_type, **powershell_options):
        """Remove (clear) an assigned Teams policy for a user (PowerShell-best)."""

        script = r"""
$type = ($policy_type | ForEach-Object { $_.ToString().Trim().ToLowerInvariant() })
switch ($type) {
  'messaging' { Grant-CsTeamsMessagingPolicy -Identity $user_upn -PolicyName $null }
  'meeting' { Grant-CsTeamsMeetingPolicy -Identity $user_upn -PolicyName $null }
  'calling' { Grant-CsTeamsCallingPolicy -Identity $user_upn -PolicyName $null }
  default { throw "Unknown policy_type '$policy_type'. Use messaging|meeting|calling." }
}
Get-CsOnlineUser -Identity $user_upn | Select-Object TeamsMessagingPolicy, TeamsMeetingPolicy, TeamsCallingPolicy
"""
        return self._get_powershell(**powershell_options).run_json(
            script,
            parameters={"user_upn": user_upn, "policy_type": policy_type},
        )

    def create_team_powershell(self, display_name, description=None, visibility=None, **powershell_options):
        """Create team powershell."""
        params = {"DisplayName": display_name, "Description": description, "Visibility": visibility}
        cmd = "New-Team" + _ps_params(params)
        return self._get_powershell(**powershell_options).run_json(cmd)

    def set_team_powershell(self, team_id, **updates):
        """Set team powershell."""
        params = {"GroupId": team_id}
        params.update(updates)
        cmd = "Set-Team" + _ps_params(params)
        return self._get_powershell().run(cmd)

    def add_team_user_powershell(self, team_id, user, role="Member", **powershell_options):
        """Add team user powershell."""
        params = {"GroupId": team_id, "User": user, "Role": role}
        cmd = "Add-TeamUser" + _ps_params(params)
        return self._get_powershell(**powershell_options).run(cmd)

    def remove_team_user_powershell(self, team_id, user, **powershell_options):
        """Remove team user powershell."""
        params = {"GroupId": team_id, "User": user}
        cmd = "Remove-TeamUser" + _ps_params(params)
        return self._get_powershell(**powershell_options).run(cmd)

    def list_team_users_powershell(self, team_id, **powershell_options):
        """List team users powershell."""
        params = {"GroupId": team_id}
        cmd = "Get-TeamUser" + _ps_params(params)
        return self._get_powershell(**powershell_options).run_json(cmd)

    def list_team_channels_powershell(self, team_id, **powershell_options):
        """List team channels powershell."""
        params = {"GroupId": team_id}
        cmd = "Get-TeamChannel" + _ps_params(params)
        return self._get_powershell(**powershell_options).run_json(cmd)

    def create_channel_powershell(self, team_id, display_name, description=None, membership_type=None, **powershell_options):
        """Create channel powershell."""
        params = {"GroupId": team_id, "DisplayName": display_name, "Description": description, "MembershipType": membership_type}
        cmd = "New-TeamChannel" + _ps_params(params)
        return self._get_powershell(**powershell_options).run_json(cmd)


class TeamsPowerShellClient(PowerShellModuleClient):
    """Client for Teams Power Shell operations."""
    def __init__(self, session=None, connect_script=None, disconnect_script=None, pwsh_path="pwsh"):
        """Initialize the instance."""
        super().__init__(session=session, pwsh_path=pwsh_path)
        self.connect_script = connect_script
        self.disconnect_script = disconnect_script

    def _connect_script(self):
        """Internal helper for connect script."""
        if self.connect_script:
            return self.connect_script
        return "Import-Module MicrosoftTeams; Connect-MicrosoftTeams"

    def _disconnect_script(self):
        """Internal helper for disconnect script."""
        return self.disconnect_script
