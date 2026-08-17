---
name: ai-agent-cli
description: >-
  Routes agents to file-based, non-interactive use of Claude Code, Codex,
  OpenCode, Antigravity, and Grok Build CLIs. Use when calling another coding
  agent from a script, building AI-calls-AI pipelines, or choosing among these
  CLIs.
---

# AI Agent CLI

## Metadata

- **Type**: Router / BestPractice
- **Role**: Root skill for vendor coding-agent CLI orchestration
- **Scope**: Expose only this root file in a workspace skill index; focused files load on demand. Do not symlink every focused file globally.

## Goal & Boundaries

### Goal

Route orchestration to a vendor coding-agent CLI (instead of a raw model API) when execution requires a tool loop, filesystem access, or subscription quota, ensuring all interactions follow a verifiable file-based contract.

### When to Use

Use a CLI agent when at least one condition holds:
- The task requires multiple tool calls or several minutes.
- The child process must read and write local files.
- You want subscription quota instead of an API key.
- You need an audit trail of disk modifications.

### Boundaries & Out of Scope

- **In-process threshold**: Do not use a CLI agent for a single short completion doable in-process.
- **Interactive interfaces**: Interactive TUIs are out of scope.
- **Invented commands**: Subcommands like `agy run`, `claude exec`, or `grok print` do not exist and are prohibited.
- **Subagent distinction**: Do not treat a same-brand subagent as the vendor CLI.
- **Hygiene & privacy**: Never commit prompt, result, or log files that may contain task text or account metadata.

## Focused Skills & Routing

Load this root file first. Load exactly one focused file before constructing a command.

| CLI | Command | Focused Skill | Primary Preference / Fit |
|---|---|---|---|
| Claude Code | `claude -p` | [`claude_code.md`](./claude_code.md) | Deep file-aware reasoning on Anthropic |
| Codex | `codex exec` | [`codex_cli.md`](./codex_cli.md) | Structured last-message / JSON Schema automation |
| OpenCode | `opencode run` | [`opencode_cli.md`](./opencode_cli.md) | Provider-agnostic model choice, or an HTTP server |
| Antigravity | `agy --print` | [`antigravity_cli.md`](./antigravity_cli.md) | Gemini via an Antigravity subscription |
| Grok Build | `grok -p` / `grok --prompt-file` | [`grok_cli.md`](./grok_cli.md) | Grok via an xAI / SuperGrok subscription |

Preferences are starting points, not a ranking. If the user named a CLI, use that one.

## Acceptance Criteria

An AI-calls-AI invocation succeeds only when all verifiable conditions are met:

1. **Process Exit**: The child process exits with code 0.
2. **Artifact Verification**: The designated result file exists, is non-empty, and satisfies all task-specific hard checks (tokens, schema, required URLs). A fluent stdout summary is not a fallback product.
3. **Execution Auditability**: The wrapper can demonstrate:
   - The exact command line executed
   - Paths of prompt file, result file, and logs
   - Process exit code
   - Evidence the result file was read back, not just that the process started

## Enabling Guidance & Execution Contract

### File-Response Contract

All production calls use files:
- Write the full task to a prompt file. Keep the argv prompt short: "read this file, follow it, write the result there." Long bodies belong in the prompt file.
- Tell the child to write the complete product to a result path.
- Capture stdout, stderr, and any vendor log file separately.
- Clean NULs out of prompt strings (`replace('\0', '')`) before handing them to a subprocess.

### Wait Model & Process Lifetime

- The wait mechanism is process lifetime, not `sleep`. `claude -p`, `codex exec`, `opencode run`, `agy --print`, and `grok -p` stay up until the agent turn ends. Set the wrapper timeout high enough and wait for exit.
- A vendor slash command that returns immediately (Grok `/deep-research`) is not a completed turn; see [`grok_cli.md`](./grok_cli.md).

### Workspace Isolation & Nesting Bounds

- Start the child in a directory that contains only the inputs it should see. A sandbox flag does not keep secrets in sibling files out of the model context.
- Do not nest CLI-agent wrappers without a bound. One orchestrator plus one child CLI is the default. A third layer should be an explicit exception.
