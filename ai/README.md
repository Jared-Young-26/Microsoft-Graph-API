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