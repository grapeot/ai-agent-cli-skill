---
name: ai-agent-cli
description: >-
  Routes agents to file-based, non-interactive use of Claude Code, Codex,
  OpenCode, Antigravity, and Grok Build CLIs. Use when calling another coding
  agent from a script, building AI-calls-AI pipelines, or choosing among these
  CLIs.
---

# AI Agent CLI

Call a vendor coding-agent CLI instead of a raw model API when the work needs a tool loop, a filesystem, or a subscription quota. Load this file first. Load one focused file before constructing a command.

## When to use

Use a CLI agent when at least one of these is true:

- The task will take multiple tool calls or several minutes
- The child must read and write local files
- You want subscription quota instead of an API key
- You need an audit trail of what changed on disk

Do not use a CLI agent for a single short completion you can do in-process.

## Focused files

| CLI | Command | Load |
|---|---|---|
| Claude Code | `claude -p` | [`claude_code.md`](./claude_code.md) |
| Codex | `codex exec` | [`codex_cli.md`](./codex_cli.md) |
| OpenCode | `opencode run` | [`opencode_cli.md`](./opencode_cli.md) |
| Antigravity | `agy --print` | [`antigravity_cli.md`](./antigravity_cli.md) |
| Grok Build | `grok -p` / `grok --prompt-file` | [`grok_cli.md`](./grok_cli.md) |

Expose only this root file in a workspace skill index. Do not symlink every focused file globally.

## Which CLI

| Need | Prefer |
|---|---|
| Deep file-aware reasoning on Anthropic | Claude Code |
| Structured last-message / JSON Schema automation | Codex |
| Provider-agnostic model choice, or an HTTP server | OpenCode |
| Gemini via an Antigravity subscription | Antigravity |
| Grok via an xAI / SuperGrok subscription | Grok Build |

These are starting points, not a ranking. If the user named a CLI, use that one.

## File-response contract

All production calls use files:

1. Write the full task to a prompt file.
2. Tell the child to write the complete product to a result path.
3. Capture stdout, stderr, and any vendor log file separately.

The wait mechanism is process lifetime, not `sleep`. `claude -p`, `codex exec`, `opencode run`, `agy --print`, and `grok -p` stay up until the agent turn ends. Set the wrapper timeout high enough and wait for exit. A vendor slash command that returns immediately (Grok `/deep-research`) is not a completed turn; see [`grok_cli.md`](./grok_cli.md).

The call succeeded only when the process exits 0 **and** the result file exists, is non-empty, and satisfies the task's hard checks (tokens, schema, required URLs). A fluent stdout summary is not a fallback product.

Keep the argv prompt short: "read this file, follow it, write the result there." Long bodies belong in the prompt file.

Start the child in a directory that contains only the inputs it should see. A sandbox flag does not keep secrets in sibling files out of the model context.

## AI-calls-AI acceptance

A wrapper is done when it can show:

- The exact command that ran
- Paths of the prompt file, result file, and logs
- Exit code
- Evidence the result file was read back, not just that the process started

Do not nest CLI-agent wrappers without a bound. One orchestrator plus one child CLI is the default. A third layer should be an explicit exception.

Clean NULs out of prompt strings (`replace('\0', '')`) before handing them to a subprocess.

## Out of scope

- Interactive TUIs
- Invented subcommands (`agy run`, `claude exec`, `grok print`)
- Treating a same-brand subagent as the vendor CLI
- Committing prompt/result/log files that may contain task text or account metadata
