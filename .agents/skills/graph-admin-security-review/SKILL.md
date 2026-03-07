---
name: graph-admin-security-review
description: Use this skill for security, authentication, token, permission, secret, injection, data-exposure, or trust-boundary review in the Microsoft Graph Admin Studio repository. Do not use it for normal feature implementation unless the task is explicitly security-focused.
---


# Graph Admin Security Review

Use this skill for static review and security-oriented reasoning.

## Read first

Always:
- `AGENTS.md`
- `/ai/constraints.md`
- `/ai/active_task.md`

Usually:
- `/ai/handoff.md`
- `/ai/architecture.md`
- `/ai/repo_map.md`
- `/ai/reviews/security_report.md`

## Focus areas

Review the current workstream and relevant code for:
- authentication flow mistakes
- over-broad permissions or Graph scope usage
- token handling mistakes
- secret exposure in code, logs, or storage
- DOM injection / XSS risks
- unsafe HTML rendering
- unsafe URL or redirect handling
- storage of sensitive data in local/session storage
- logging of PII, tokens, or internal secrets
- trust-boundary confusion between frontend and backend

## Required workflow

1. Define the scope reviewed.
2. Map the relevant trust boundaries.
3. Look for concrete issues, not vague fear.
4. Separate:
   - confirmed findings
   - plausible risks
   - non-issues already ruled out
5. Update `/ai/reviews/security_report.md`.
6. If the review changes the recommended next step, update `/ai/handoff.md` and `/ai/status.md`.

## Output requirements

End with:
- confirmed findings by severity
- plausible risks needing follow-up
- evidence or affected files
- recommended mitigations
- residual risk

