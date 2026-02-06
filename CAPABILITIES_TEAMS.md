# CAPABILITIES_TEAMS.md
## Graph Admin Studio — Teams Module (Ruthless Spec)

### North Star
Teams must explain:
- Why users can/can’t chat, meet, call
- Which policy applies
- How to safely fix policy drift

---

## 1) Permissions

Graph (app permissions):
- Group.Read.All
- Channel.Read.All
- ChannelMessage.Read.All
- Team.ReadBasic.All
- TeamMember.Read.All
- Policy.Read.All
- Policy.ReadWrite.Teams (only if assigning)

PowerShell:
- MicrosoftTeams module

---

## 2) Context Keys

- context.team_id
- context.channel_id
- context.user_upn
- context.policy_name

---

## 3) Capability Map

### 3.1 Teams & Channels

Discover:
- teams.list_teams
- teams.get_team
- teams.list_channels
- teams.list_team_members

Change:
- teams.create_channel (Caution)
- teams.add_member (Caution)
- teams.remove_member (Dangerous)

### 3.2 Policies (PS-best)

Inspect:
- teams.ps_list_policies
- teams.ps_get_user_policy_assignments

Change:
- teams.ps_assign_user_policy (Caution)
- teams.ps_remove_user_policy (Dangerous)

---

## 4) Symptom Templates

- teams.user_cannot_chat
- teams.user_cannot_meet
- teams.policy_not_applying

---

## 5) Testing

- Policy assignments reflect immediately
- Context binds user/team automatically

