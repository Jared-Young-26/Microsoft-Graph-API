# Graph Admin Studio Codex Pipeline Playbook

This guide gives you a **full, copy-pasteable setup** for using Codex in a disciplined, scalable way on the Microsoft Graph API / Graph Admin Studio project.

The goal is to stop using one giant context-poisoned thread and replace it with a **clean, repeatable AI delivery pipeline** inside your repo.

---

# 1. What You Are Building

You are not building a custom automation framework first.

You are building a **repo-native operating system for Codex work**.

That means:

- a stable `/ai` folder in the repo
- clear architecture and constraint documents
- role-specific prompts
- handoff documents between threads
- thread rules for when to use Local vs Worktree
- a repeatable workflow for architecture, implementation, testing, debugging, review, and refactoring

This works **inside the Codex GUI on your Mac** using:

- separate threads
- plan mode when needed
- handoff
- repo access
- optional tools like Playwright

---

# 2. Big Picture Workflow

Your standard delivery pipeline should be:

```text
Architect -> Implement -> Test -> Debug -> Security Review -> Refactor -> Merge
```

Each stage should use either:

- a new Codex thread, or
- a handoff into a clean follow-on thread

Each stage should read from the `/ai` folder and produce an artifact back into `/ai`.

---

# 3. Repo Folder Structure to Add

Create this exact folder structure in your repo:

```text
/ai
  README.md
  architecture.md
  constraints.md
  repo_map.md
  backlog.md
  active_task.md
  task_breakdown.md
  handoff.md
  thread_log.md
  prompts/
    architect.md
    implementer.md
    tester.md
    debugger.md
    security_reviewer.md
    refactorer.md
    documenter.md
  reviews/
    test_report.md
    security_report.md
    refactor_report.md
  plans/
    current_plan.md
    future_work.md
```

---

# 4. Step-by-Step Setup From Zero

## Step 1 - Create the `/ai` folder

At the root of the Microsoft Graph API repo, create the `/ai` folder and all subfolders/files listed above.

## Step 2 - Paste in the starter contents below

Every file below has starter content you can copy directly.

## Step 3 - Commit only the AI operating documents

Make a small commit such as:

```text
git add ai
git commit -m "Add Codex workflow and AI project operating docs"
```

## Step 4 - Your next Codex thread should only do repo-mapping

Do **not** jump into feature work yet.

Your first clean thread should update:

- `/ai/repo_map.md`
- `/ai/architecture.md`
- `/ai/backlog.md`

based on the project as it exists today.

## Step 5 - Start using role-based threads only

From that point forward, each thread has exactly one role and one mission.

---

# 5. File Contents

## `/ai/README.md`

```markdown
# AI Workflow Operating System

This folder contains the working memory and operating rules for using Codex on this repository.

## Purpose

The goal is to keep AI work structured, deterministic, and reviewable.

This repo should not rely on one long Codex conversation. Instead, work should be split into clean phases:

1. Architecture
2. Implementation
3. Testing
4. Debugging
5. Security Review
6. Refactor
7. Documentation

## Rules

- Always read `constraints.md` before changing code.
- Always read `active_task.md` before starting work.
- Always update `handoff.md` when stopping a thread.
- Always update `thread_log.md` after major work.
- Do not invent architecture if `architecture.md` already defines it.
- Do not modify unrelated files.
- Prefer small, reviewable changes.

## Primary Files

- `architecture.md` -> target architecture and design principles
- `constraints.md` -> hard guardrails
- `repo_map.md` -> current file/module map
- `backlog.md` -> known work items
- `active_task.md` -> the current focus
- `task_breakdown.md` -> implementation steps for the current task
- `handoff.md` -> summary passed to next thread
- `thread_log.md` -> thread history and outcomes
```

## `/ai/constraints.md`

```markdown
# Constraints

These are hard rules for Codex work in this repository.

## Global Constraints

1. Do not rewrite the project into a framework unless explicitly instructed.
2. Preserve the current backend/API contracts unless the task explicitly requires backend changes.
3. Prefer incremental refactors over large rewrites.
4. Keep changes scoped to the active task.
5. Do not rename stable files, IDs, selectors, or interfaces without documenting the reason.
6. Preserve existing functionality unless the task explicitly changes behavior.
7. Avoid introducing new dependencies unless there is a strong justification.
8. Favor readability and maintainability over cleverness.
9. Update relevant AI documents when architecture or workflow assumptions change.
10. If the repo contains generated or mirrored content, do not manually edit those files unless explicitly told to do so.

## Graph Admin Studio Specific Constraints

1. Keep the portal in vanilla HTML/CSS/JS unless explicitly approved otherwise.
2. Do not churn backend plumbing unnecessarily.
3. Preserve stable workspace identifiers and data attributes.
4. Prefer templating only where repetition is real and semantics remain clear.
5. Preserve the distinct identity of bespoke modules that should not be flattened into generic shells.
6. Do not break boot order or initialization assumptions.
7. If a hard dependency exists between files, document it explicitly in `architecture.md` and `repo_map.md`.

## Safety Rules for Changes

Before making edits, verify:

- What files are in scope?
- What files are out of scope?
- What behavior must remain unchanged?
- What IDs/classes/selectors/contracts must remain stable?

If any of the above are unclear, document assumptions in the handoff instead of improvising.
```

## `/ai/architecture.md`

```markdown
# Architecture

This file describes the intended architecture of the repository as it exists today and where it is going.

## Project Mission

Graph Admin Studio is intended to become a comprehensive Microsoft 365 + hybrid troubleshooting and action dashboard, with a broad catalog of modules, tools, and guided workflows.

## Current High-Level Direction

- Frontend remains vanilla HTML/CSS/JS.
- Schema and boot logic should be explicit and predictable.
- Repeated service/toolkit shells should be templated only where it reduces duplication without hiding behavior.
- Bespoke modules remain bespoke when their UX or logic is meaningfully different.
- Workspace-stable IDs and data attributes should exist early so future orchestration remains stable.

## Architectural Principles

1. Semantic clarity over abstraction theater.
2. Templating for repeated shells, not for everything.
3. Explicit boot dependencies.
4. Stable DOM hooks for orchestration and testing.
5. Small refactors that preserve behavior.
6. Clear split between schema, render, boot, workflow logic, and output handling.

## Mandatory Boot / Load Assumptions

Document all required file ordering and boot dependencies here.

Example:
- `portal_schema.js` must load before `app.js`.
- `app.js` should fail loudly if required schema is not present.

## Known Future State

This section should be updated over time as the platform evolves toward:

- cleaner section semantics
- generated shells for repeated tool blocks
- preserved bespoke flows for special modules
- stronger testability
- more stable extension points
```

## `/ai/repo_map.md`

```markdown
# Repo Map

This file should describe the real repository structure and responsibilities.

## How to Maintain This File

For each major file or folder, document:

- path
- responsibility
- whether it is core, optional, generated, or legacy
- known dependencies
- whether stable selectors/IDs/contracts exist

## Starter Template

### Root
- `README.md` -> project overview
- `admin_gui/` -> frontend portal code
- `...` -> fill this in based on the real repo

### Example Entry
#### `admin_gui/index.html`
- Role: main portal shell
- Type: core frontend entry point
- Notes: contains repeated toolkit + runner + output triplets
- Stability: DOM structure should be refactored carefully

#### `admin_gui/app.js`
- Role: bootstraps portal behavior
- Type: core boot logic
- Dependencies: must not run before schema is loaded
- Stability: high importance

#### `admin_gui/portal_schema.js`
- Role: defines section/module metadata
- Type: schema
- Dependencies: must load before `app.js`
- Stability: high importance
```

## `/ai/backlog.md`

```markdown
# Backlog

This file contains candidate work items.

## Prioritization Labels

- P0 -> critical / blocking
- P1 -> high value
- P2 -> useful
- P3 -> later / exploratory

## Template

### [P1] Example Task Title
- Goal:
- Why it matters:
- In scope:
- Out of scope:
- Dependencies:
- Risks:
- Done when:

## Starter Items

### [P0] Build accurate repo map
- Goal: document the real current structure of the repo
- Why it matters: all future Codex threads need shared ground truth
- In scope: `/ai/repo_map.md`, `/ai/architecture.md`, `/ai/backlog.md`
- Out of scope: implementation changes
- Dependencies: read current repo
- Risks: stale documentation
- Done when: major modules and dependencies are documented

### [P1] Harden frontend boot sequence
- Goal: ensure boot fails loudly when required schema is missing
- Why it matters: prevents silent breakage and hidden ordering bugs
- In scope: frontend boot dependency checks
- Out of scope: unrelated UI cleanup
- Dependencies: repo map, architecture review
- Risks: false positives if boot assumptions are misunderstood
- Done when: dependency is enforced and documented

### [P1] Reduce repeated toolkit shell duplication
- Goal: centralize repeated service shell rendering where repetition is real
- Why it matters: easier maintenance and less drift
- In scope: repeated shell rendering only
- Out of scope: bespoke workflow modules that need custom structure
- Dependencies: architecture signoff
- Risks: flattening distinct modules accidentally
- Done when: duplicated shell blocks are reduced without losing semantics
```

## `/ai/active_task.md`

```markdown
# Active Task

## Title
Initial AI workflow setup and repo mapping

## Goal
Create the AI operating structure and document the real Graph Admin Studio repo so future Codex threads have stable context.

## In Scope
- `/ai/*` documentation
- repo mapping
- architecture clarification
- backlog seeding

## Out of Scope
- feature implementation
- major refactors
- test writing
- UI cleanup changes

## Inputs
- existing repository structure
- current Graph Admin Studio plan
- current frontend files and boot logic

## Deliverables
- updated `repo_map.md`
- updated `architecture.md`
- updated `backlog.md`
- clear handoff to implementation planning

## Done When
The AI docs accurately describe the repo and the next implementation thread can begin without guessing.
```

## `/ai/task_breakdown.md`

```markdown
# Task Breakdown

Use this file to define exact implementation steps for the active task.

## Template
1. Inspect current repo structure
2. Identify core files/folders
3. Document file responsibilities
4. Document load-order dependencies
5. Record repeated structures and bespoke modules
6. Update architecture doc
7. Seed backlog with prioritized tasks
8. Write handoff

## Current Breakdown
1. Create `/ai` operating files
2. Inspect current Graph Admin Studio structure
3. Map frontend entry points and schema/boot dependencies
4. Document repeated shell patterns
5. Identify bespoke modules that must remain bespoke
6. Update backlog with the next 5-10 high-value tasks
7. Prepare architecture-thread handoff
```

## `/ai/handoff.md`

```markdown
# Handoff

## Thread Name
TBD

## Role
TBD

## What Was Completed
- TBD

## Files Touched
- TBD

## Decisions Made
- TBD

## Constraints Reconfirmed
- TBD

## Open Questions
- TBD

## Recommended Next Thread
- TBD

## Copy/Paste Prompt for Next Thread
TBD
```

## `/ai/thread_log.md`

```markdown
# Thread Log

Use this file to keep a lightweight record of Codex sessions.

## Template
### YYYY-MM-DD - Thread Name
- Role:
- Objective:
- Outcome:
- Files touched:
- Risks / follow-up:

## Starter Entry
### 2026-03-06 - AI workflow bootstrap
- Role: human setup / project operating system
- Objective: create the `/ai` structure and establish disciplined Codex usage
- Outcome: initial workflow docs created
- Files touched: `/ai/*`
- Risks / follow-up: docs must be updated to match real repo state before implementation threads begin
```

---

# 6. Prompt Files

## `/ai/prompts/architect.md`

```markdown
ROLE: Software Architect

You are the architecture agent for this repository.

Your job is to design or refine structure, not to rush into coding.

Read first:
- `/ai/README.md`
- `/ai/constraints.md`
- `/ai/architecture.md`
- `/ai/repo_map.md`
- `/ai/active_task.md`
- `/ai/task_breakdown.md`

Rules:
1. Do not implement code unless explicitly asked.
2. Identify dependencies, file responsibilities, invariants, and risks.
3. Preserve existing constraints.
4. Prefer incremental architecture over sweeping rewrites.
5. Produce concrete deliverables, not vague advice.

Required Output:
- recommended architecture updates
- exact file/module responsibilities
- risks and tradeoffs
- implementation-ready task list
- suggested next thread prompt
```

## `/ai/prompts/implementer.md`

```markdown
ROLE: Implementation Engineer

You are the implementation agent.

Read first:
- `/ai/README.md`
- `/ai/constraints.md`
- `/ai/architecture.md`
- `/ai/repo_map.md`
- `/ai/active_task.md`
- `/ai/task_breakdown.md`
- `/ai/handoff.md`

Rules:
1. Implement only the active task.
2. Do not redesign architecture unless the task explicitly asks for it.
3. Do not modify unrelated files.
4. Preserve stable IDs, contracts, and behavior unless the task explicitly changes them.
5. Keep changes reviewable.
6. Update `/ai/handoff.md` and `/ai/thread_log.md` when done.

Required Output:
- completed code changes
- short explanation of what changed
- known risks
- recommended test focus
```

## `/ai/prompts/tester.md`

```markdown
ROLE: Test Engineer

You are the testing agent.

Read first:
- `/ai/README.md`
- `/ai/constraints.md`
- `/ai/architecture.md`
- `/ai/repo_map.md`
- `/ai/active_task.md`
- `/ai/handoff.md`

Rules:
1. Test the implemented change, not the whole universe.
2. Focus on behavior, regressions, and edge cases.
3. Use Playwright only if browser-level validation is appropriate.
4. Document all failures clearly.
5. Do not silently widen scope.

Required Output:
- test plan
- test cases
- failures found
- recommended bug-fix priorities
- updates to `/ai/reviews/test_report.md`
```

## `/ai/prompts/debugger.md`

```markdown
ROLE: Debug Engineer

You are the debugging agent.

Read first:
- `/ai/README.md`
- `/ai/constraints.md`
- `/ai/architecture.md`
- `/ai/repo_map.md`
- `/ai/handoff.md`
- `/ai/reviews/test_report.md`

Rules:
1. Find root cause before changing code.
2. Keep fixes minimal and targeted.
3. Do not rewrite large areas to fix a local bug.
4. Preserve intended architecture.

Required Output:
- root cause
- exact fix applied
- why the bug happened
- regression risks
- updated handoff
```

## `/ai/prompts/security_reviewer.md`

```markdown
ROLE: Security Reviewer

You are the security review agent.

Read first:
- `/ai/README.md`
- `/ai/constraints.md`
- `/ai/architecture.md`
- `/ai/repo_map.md`
- `/ai/handoff.md`

Review for:
- unsafe DOM insertion
- injection risk
- credential handling
- insecure assumptions
- overexposed admin actions
- missing validation
- fragile privilege assumptions

Rules:
1. Do not invent vulnerabilities without evidence.
2. Distinguish confirmed issues from cautionary notes.
3. Keep findings actionable.

Required Output:
- findings by severity
- exact file locations
- remediation advice
- updates to `/ai/reviews/security_report.md`
```

## `/ai/prompts/refactorer.md`

```markdown
ROLE: Refactor Engineer

You are the refactoring agent.

Read first:
- `/ai/README.md`
- `/ai/constraints.md`
- `/ai/architecture.md`
- `/ai/repo_map.md`
- `/ai/handoff.md`

Rules:
1. Refactor without changing behavior.
2. Prefer readability and maintainability.
3. Do not mix refactor work with feature work unless explicitly instructed.
4. Preserve stable interfaces.

Required Output:
- what was simplified
- what stayed behaviorally identical
- any areas still carrying technical debt
- updates to `/ai/reviews/refactor_report.md`
```

## `/ai/prompts/documenter.md`

```markdown
ROLE: Technical Documenter

You are the documentation agent.

Read first:
- `/ai/README.md`
- `/ai/constraints.md`
- `/ai/architecture.md`
- `/ai/repo_map.md`
- `/ai/handoff.md`

Rules:
1. Document what actually exists.
2. Do not describe wishful architecture as if it already exists.
3. Keep docs crisp and useful.

Required Output:
- updated docs
- setup notes
- future contributors guidance
```

---

# 7. Review File Starters

## `/ai/reviews/test_report.md`

```markdown
# Test Report

## Scope
TBD

## Environment
TBD

## Cases Executed
- TBD

## Results
- PASS: TBD
- FAIL: TBD

## Notes
- TBD
```

## `/ai/reviews/security_report.md`

```markdown
# Security Report

## Scope
TBD

## Findings
### High
- None yet

### Medium
- None yet

### Low
- None yet

## Notes
- TBD
```

## `/ai/reviews/refactor_report.md`

```markdown
# Refactor Report

## Scope
TBD

## Improvements Made
- TBD

## Behavior Preserved
- TBD

## Remaining Technical Debt
- TBD
```

---

# 8. Plans File Starters

## `/ai/plans/current_plan.md`

```markdown
# Current Plan

## Active Objective
Bootstrap disciplined Codex workflow and document the current repo accurately.

## Sequence
1. Build `/ai` folder
2. Map repo
3. Update architecture
4. Seed backlog
5. Begin first architecture thread for current Graph Admin Studio cleanup work
```

## `/ai/plans/future_work.md`

```markdown
# Future Work

Potential future expansions for the AI workflow:

- PR review prompt packs
- release checklist prompt
- migration planning prompt
- issue triage prompt
- automatic changelog generation
- repo-specific test templates
- security checklist for admin actions
```

---

# 9. How to Use This in Codex Day to Day

## Core Rule

Never start with “continue from everything we talked about.”

That phrase is context goblin food.

Instead, start with:

- the role
- the current task
- the files to read
- the files allowed to change
- the deliverable

---

# 10. Thread Taxonomy

Use threads like these:

## Architecture Thread
Use when:
- defining structure
- planning refactors
- deciding file/module responsibilities
- identifying risks before implementation

## Implementation Thread
Use when:
- writing code for one approved task
- updating a bounded set of files

## Test Thread
Use when:
- validating one implementation
- writing browser checks or behavioral tests

## Debug Thread
Use when:
- a failure exists
- you have evidence to analyze

## Security Review Thread
Use when:
- a change affects admin actions, rendering, data flow, auth assumptions, or anything spicy

## Refactor Thread
Use when:
- code already works and now needs cleanup

---

# 11. When to Start a New Thread

Start a new thread when:

1. the goal changes
2. the role changes
3. the task becomes ambiguous
4. the model starts re-litigating old choices
5. the thread has accumulated too much unrelated history
6. you move from planning to coding
7. you move from coding to testing
8. you need a clean review pass

If the task can be described by a different job title, it should probably be a new thread.

---

# 12. Local vs Worktree Strategy

Use **Local** when:
- small, low-risk edits
- documentation changes
- scoped changes you are actively supervising

Use **Worktree** when:
- parallel experiments
- risky refactors
- testing multiple approaches
- isolating one feature stream from another

Recommended rule:

- Architecture threads: Local is fine
- Implementation for risky refactors: Worktree preferred
- Test/debug/security review: usually same worktree as implementation

---

# 13. When to Use Plan Mode

Use Plan mode when:
- architecture decisions matter
- many files may be involved
- boot sequence or contracts may be affected
- refactor scope is nontrivial
- you want a task list before code begins

Do not use Plan mode for tiny edits like:
- renaming a label
- changing one CSS class
- fixing an obvious typo

Recommended pattern:

1. Plan mode for architecture or multi-file change
2. Review plan
3. Approve scope
4. Start implementation thread

---

# 14. When to Enable Playwright

Enable Playwright when:
- UI behavior matters
- the task affects rendering
- state transitions matter
- click flows matter
- you need browser validation

Do not enable it just because more tools feel cool.

More tools do not automatically make Codex smarter. They just give it more levers to yank, sometimes with all the grace of a caffeinated raccoon.

---

# 15. Standard Operating Thread Prompt Templates

## A. Repo Mapping Thread

```markdown
ROLE: Software Architect

Read these files first:
- /ai/README.md
- /ai/constraints.md
- /ai/architecture.md
- /ai/repo_map.md
- /ai/backlog.md
- /ai/active_task.md
- /ai/task_breakdown.md

Task:
Inspect the current repository and update the AI operating docs so they accurately reflect the real current state of the Graph Admin Studio project.

Focus only on:
- repo structure
- file responsibilities
- boot/load order dependencies
- repeated shell patterns
- bespoke modules that should remain bespoke
- backlog seeding

Do not implement feature changes yet.

Files allowed to change:
- /ai/repo_map.md
- /ai/architecture.md
- /ai/backlog.md
- /ai/handoff.md
- /ai/thread_log.md

Deliverables:
- updated repo map
- updated architecture notes
- prioritized backlog entries
- recommended next implementation thread prompt
```

## B. Architecture Planning Thread

```markdown
ROLE: Software Architect

Read these files first:
- /ai/README.md
- /ai/constraints.md
- /ai/architecture.md
- /ai/repo_map.md
- /ai/backlog.md
- /ai/active_task.md
- /ai/task_breakdown.md
- /ai/handoff.md

Task:
Design the implementation plan for the active Graph Admin Studio refactor task.

Requirements:
- preserve vanilla HTML/CSS/JS architecture
- preserve backend/API behavior
- identify repeated shell structures that can be templated
- identify modules that should remain bespoke
- preserve stable workspace block identifiers and hooks
- document file-level responsibilities and risks

Do not implement code.

Files allowed to change:
- /ai/architecture.md
- /ai/task_breakdown.md
- /ai/handoff.md
- /ai/thread_log.md
- /ai/plans/current_plan.md

Deliverables:
- refined architecture section
- concrete implementation task list
- risk notes
- exact copy-paste prompt for the implementation thread
```

## C. Implementation Thread

```markdown
ROLE: Implementation Engineer

Read these files first:
- /ai/README.md
- /ai/constraints.md
- /ai/architecture.md
- /ai/repo_map.md
- /ai/active_task.md
- /ai/task_breakdown.md
- /ai/handoff.md

Task:
Implement the active task exactly as specified.

Requirements:
- keep changes scoped
- do not redesign the architecture
- preserve stable IDs, hooks, selectors, and backend contracts
- touch only files required for this task
- keep the diff reviewable

Files allowed to change:
- only files directly required for the active task
- /ai/handoff.md
- /ai/thread_log.md

Deliverables:
- implementation changes
- concise summary of edits
- known risks
- recommended test cases
```

## D. Test Thread

```markdown
ROLE: Test Engineer

Read these files first:
- /ai/README.md
- /ai/constraints.md
- /ai/architecture.md
- /ai/repo_map.md
- /ai/handoff.md
- /ai/reviews/test_report.md

Task:
Validate the implementation from the previous thread.

Focus on:
- behavior correctness
- regressions
- DOM stability
- workflow behavior
- output/render correctness

Use Playwright if browser validation is helpful.

Files allowed to change:
- test files if needed
- /ai/reviews/test_report.md
- /ai/handoff.md
- /ai/thread_log.md

Deliverables:
- executed test plan
- pass/fail results
- root-cause notes for failures
- recommended debugger thread prompt if needed
```

## E. Debug Thread

```markdown
ROLE: Debug Engineer

Read these files first:
- /ai/README.md
- /ai/constraints.md
- /ai/architecture.md
- /ai/repo_map.md
- /ai/handoff.md
- /ai/reviews/test_report.md

Task:
Fix the failing behavior identified in the test report.

Requirements:
- identify root cause first
- make the smallest correct fix
- preserve intended architecture
- do not widen scope

Files allowed to change:
- only files needed for the bug fix
- /ai/handoff.md
- /ai/thread_log.md
- /ai/reviews/test_report.md

Deliverables:
- root cause
- exact fix
- regression risk notes
- recommendation for re-test scope
```

## F. Security Review Thread

```markdown
ROLE: Security Reviewer

Read these files first:
- /ai/README.md
- /ai/constraints.md
- /ai/architecture.md
- /ai/repo_map.md
- /ai/handoff.md
- /ai/reviews/security_report.md

Task:
Review the implemented change for security risks.

Focus on:
- unsafe DOM insertion
- injection possibilities
- auth/authorization assumptions
- admin-action exposure
- unvalidated inputs
- fragile client-side trust assumptions

Files allowed to change:
- /ai/reviews/security_report.md
- /ai/handoff.md
- /ai/thread_log.md

Deliverables:
- severity-ranked findings
- evidence-based notes
- remediation recommendations
```

## G. Refactor Thread

```markdown
ROLE: Refactor Engineer

Read these files first:
- /ai/README.md
- /ai/constraints.md
- /ai/architecture.md
- /ai/repo_map.md
- /ai/handoff.md
- /ai/reviews/refactor_report.md

Task:
Refactor the completed implementation for readability and maintainability without changing behavior.

Requirements:
- no behavior changes
- preserve stable contracts
- keep the diff understandable

Files allowed to change:
- only files in approved refactor scope
- /ai/reviews/refactor_report.md
- /ai/handoff.md
- /ai/thread_log.md

Deliverables:
- simplified code
- note of preserved behavior
- remaining technical debt
```

---

# 16. Handoff Template to Reuse Between Threads

Paste this into `/ai/handoff.md` at the end of each thread:

```markdown
# Handoff

## Thread Name
[fill in]

## Role
[Architect / Implementer / Tester / Debugger / Security Reviewer / Refactorer]

## Objective
[fill in]

## Completed
- [item]
- [item]

## Files Changed
- [path]
- [path]

## Decisions Made
- [decision]
- [decision]

## Constraints Reconfirmed
- [constraint]
- [constraint]

## Known Risks
- [risk]
- [risk]

## Recommended Next Thread
[fill in]

## Copy/Paste Prompt for Next Thread
[paste exact next-thread prompt here]
```

---

# 17. First Real Sequence for Graph Admin Studio

Here is the exact order I recommend for your current project.

## Thread 1 - Repo Mapping
Goal:
Get `/ai/repo_map.md`, `/ai/architecture.md`, and `/ai/backlog.md` aligned to the real project state.

Use prompt:
`/ai/prompts/architect.md` + the “Repo Mapping Thread” template above.

## Thread 2 - Architecture Pass for Current Cleanup Plan
Goal:
Translate the current UI cleanup plan into a concrete implementation sequence.

Expected outputs:
- exact files to touch
- exact repeated shells to template
- exact bespoke modules to preserve
- exact boot guard change if needed

## Thread 3 - Implementation: Boot Guard
Goal:
Implement the hard boot guard for schema-before-app behavior.

## Thread 4 - Test: Boot Guard
Goal:
Validate failure mode and successful boot path.

## Thread 5 - Implementation: Repeated Shell Templating
Goal:
Template repeated toolkit + runner + output shell blocks while preserving semantics.

## Thread 6 - Test: Shell Templating
Goal:
Validate rendering and stable hooks.

## Thread 7 - Security Review
Goal:
Review DOM generation and admin interactions for injection or trust mistakes.

## Thread 8 - Refactor/Polish
Goal:
Remove leftover duplication and document extension points.

---

# 18. Rules for Keeping Context Clean

1. Never let a thread drift into a second mission.
2. Never mix architecture and bug fixing in one thread unless the bug is architectural.
3. Never ask a testing thread to redesign code.
4. Never ask an implementation thread to “also clean up some other stuff while you're in there.” That way lies clown shoes and merge pain.
5. Always write the next prompt into `handoff.md` before ending the thread.
6. Keep `active_task.md` current.
7. Keep diffs small enough that you can actually review them like a grown mammal.

---

# 19. What You Do Right Now

Do these steps in order:

1. Create the `/ai` folder and all files above.
2. Paste the starter content into each file.
3. Commit the `/ai` folder.
4. Open a fresh Codex thread.
5. Use the “Repo Mapping Thread” prompt.
6. Let Codex update the AI docs to match the real Graph Admin Studio repo.
7. Review and commit that.
8. Open a new architecture thread for the current cleanup plan.
9. Use handoff into implementation.
10. Use separate test/debug/security/refactor threads after that.

That is the full disciplined setup.

Not glamorous. Very effective. A little like giving your future self a map instead of a head injury.

---

# 20. Optional Future Upgrade

Later, if you want, you can evolve this into a true automated multi-agent pipeline using external tooling such as LangGraph, AutoGen, or n8n. But do **not** start there.

Your best next move is getting this **repo-native Codex operating system** working first.

That alone will massively improve consistency, reduce thread poisoning, and let you scale work across a much larger project without turning the AI into a confused goblin with commit access.
