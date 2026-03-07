# Role Map — Threads, Skills, Modes, and Outputs

| Workstream | Preferred Skill | Mode | Speed | Use Plan Mode? | Primary inputs | Primary outputs |
|---|---|---:|---:|---:|---|---|
| Architecture / design | `$graph-admin-architect` | Local | Standard | Usually yes | `constraints.md`, `architecture.md`, `repo_map.md`, `status.md`, `backlog.md`, `plans/current_plan.md` | `architecture.md`, `repo_map.md`, `plans/current_plan.md`, `decision_log.md`, `task_breakdown.md` |
| Implementation | `$graph-admin-implement` | Worktree | Standard | Sometimes | `constraints.md`, `active_task.md`, `task_breakdown.md`, `architecture.md`, `repo_map.md` | code changes, `handoff.md`, `thread_log.md`, maybe `status.md` |
| Debugging | `$graph-admin-debug` | Worktree | Standard | Often | `constraints.md`, `active_task.md`, `handoff.md`, `task_breakdown.md`, `architecture.md` | fixes, `handoff.md`, `thread_log.md`, maybe `test_report.md` |
| Testing / validation | `$graph-admin-test-verify` | Worktree | Standard | Rarely | `active_task.md`, `task_breakdown.md`, existing tests, `handoff.md` | tests or validation output, `reviews/test_report.md`, `handoff.md` |
| Security review | `$graph-admin-security-review` | Worktree or Local | Standard | Rarely | current diff, `constraints.md`, `architecture.md`, auth-related code | `reviews/security_report.md`, `handoff.md` |
| Refactor | `$graph-admin-refactor` | Worktree | Standard | Sometimes | `active_task.md`, `architecture.md`, `repo_map.md`, current diff | cleanup diff, `reviews/refactor_report.md`, `handoff.md` |
| Doc sync | `$graph-admin-doc-sync` | Local | Fast | No | `/ai` docs, current diff, repo state | updated docs only |
| Next-task prep | `$graph-admin-next-task` | Local | Fast | No | `backlog.md`, `status.md`, `architecture.md`, `active_task.md` | updated `active_task.md`, `task_breakdown.md`, `status.md` |
| Handoff cleanup | `$graph-admin-handoff` | Local or Worktree | Fast | No | current thread state, `active_task.md`, `handoff.md` | refreshed `handoff.md`, `thread_log.md` |
| Repo triage / automation | `$graph-admin-repo-triage` | Local or Worktree | Standard | No | repo status, recent diffs, `/ai` docs | updated `status.md`, `backlog.md`, `thread_log.md`, findings summary |

## Practical default

For most day-to-day work:

1. `$graph-admin-next-task`
2. `$graph-admin-implement`
3. `$graph-admin-test-verify`
4. `$graph-admin-handoff`

That is the smallest loop that stays sane.
