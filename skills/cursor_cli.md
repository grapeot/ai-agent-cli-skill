# Cursor Agent CLI

## Metadata

- **Type**: Tool / Focused Skill
- **Target**: Non-interactive `cursor agent` invocations
- **Verified Version**: Cursor IDE launcher **3.16.17** shipping agent CLI **2026.05.01-eea359f**, verified on **2026-08-18**
- **Disambiguation**: This is Cursor's agent CLI, reached through the `cursor` launcher's `agent` subcommand. It is not the standalone `~/.local/bin/agent` binary (that one is Grok Build), and it is not the IDE itself.

## Goal & Boundaries

### Goal

Execute a Cursor agent turn non-interactively from a prompt, capture text or JSON output, and ensure the agent persists verified result artifacts to disk.

### When to Load

Load this file when the user requests Cursor / `cursor agent` CLI, or when the root skill router selects it.

### Boundaries & Authentication

- **Entry point**: `cursor agent -p` (the `-p` / `--print` flag is the headless entry; there is no `cursor exec`). The top-level `cursor` binary without `agent` just opens the IDE.
- **Authentication**: `cursor agent login` (browser challenge) or `CURSOR_API_KEY` / `--api-key` (separate API billing path). Check state with `cursor agent status`, `cursor agent about`, `cursor agent --list-models`.
- **Token storage**: macOS Keychain entries `cursor-access-token` / `cursor-refresh-token`. IDE login state (SQLite under `~/Library/Application Support/Cursor`) is **not** shared with the CLI; the CLI has its own tokens.

## Acceptance Criteria

A Cursor execution is complete and valid only when:

1. **Exit Status**: Process exits with code 0. Note: some auth and model errors also exit 0 — always also check stdout content or the error line.
2. **Artifact Verification**: If a result file was required, it exists on disk and is non-empty. A fluent stdout summary is not a substitute.
3. **JSON Conformance**: With `--output-format json`, stdout is parseable JSON with `subtype: "success"` and `is_error: false`; the `usage` block reports token counts.
4. **Identity**: `cursor agent about` shows the expected account tier before batch runs.

## Available Resources & CLI Reference

### Identity Check

```bash
cursor --version            # launcher version (3.16.17)
cursor agent about          # CLI version, account, default model
cursor agent --list-models  # model IDs available to this account
```

### Command Shapes

Single-turn with file task (preferred):

```bash
cursor agent -p "Read the complete task from /absolute/path/to/prompt.md and follow it exactly." \
  --model gemini-3.7-flash-high \
  --trust \
  --workspace /absolute/path/to/scratch \
  --output-format text
```

Structured output:

```bash
cursor agent -p "..." --output-format json
# -> {"type":"result","subtype":"success","is_error":false,
#     "result":"...","session_id":"...","usage":{...}}
```

### Key Flags

| Flag | Description & Operational Boundary |
|---|---|
| `-p` / `--print` | Headless single-turn entry; full tool access including write and shell. |
| `--output-format` | `text` (default), `json`, `stream-json`; `--stream-partial-output` for deltas (stream-json only). |
| `--mode` / `--plan` | `plan` = read-only planning; `ask` = Q&A read-only. |
| `--model` | Model ID from `--list-models`. Always pass explicitly. |
| `--trust` | Trust the workspace without prompting (print mode only). Required for smooth headless runs. |
| `--sandbox` | `enabled` / `disabled`; overrides config. |
| `-f` / `--force` / `--yolo` | Auto-approve commands unless explicitly denied. |
| `--workspace` | Working directory (defaults to cwd). |
| `-w` / `--worktree [name]` | Isolated git worktree at `~/.cursor/worktrees/...`; `--worktree-base` picks the base ref. |
| `--resume [chatId]` / `--continue` | Session resume; `ls` lists chats. |
| `--api-key` / `CURSOR_API_KEY` | API-key auth (separate billing path from subscription). |

Other subcommands: `mcp` (manage MCP servers), `create-chat`, `update`, `install-shell-integration`, `generate-rule`, `logout`.

### Models (verified 2026-08-18, Ultra tier)

Account-dependent. Representative IDs:

- `auto` (default), `composer-1` (CLI default), `composer-2.5`
- `gemini-3.7-flash-high`, `gemini-3.7-flash-medium`, `gemini-3.7-flash-low` — **verified working end-to-end** (file task + JSON output)
- `gemini-3.6-flash-*`, `gemini-3.1-pro`
- Claude family `claude-opus-5-*` / `claude-sonnet-5-*`, GPT family `gpt-5.x-*`, `cursor-grok-4.6-*`, `kimi-k3-*`, `glm-5.2-*`

### "Fast" is a model-ID suffix, not a switch

There is no `--fast` flag. Speed variants are separate model IDs with a `-fast` suffix: `composer-2.5` vs `composer-2.5-fast`, `cursor-grok-4.6-high` vs `cursor-grok-4.6-high-fast`.

Two facts verified on 2026-08-18:

1. **Gemini 3.7 Flash has no `-fast` variant at all.** Requesting `gemini-3.7-flash-high-fast` fails with the full available-model list. Its effort levels are the `-low` / `-medium` / `-high` suffixes.
2. **`-fast` routes were broken at test time**: `composer-2.5-fast` and `cursor-grok-4.6-medium-fast` both failed with connection retries against Cursor's agent relay endpoint (`agentn.global.api5.cursor.sh`), while base models on the same account worked. Retries did not help. Treat `-fast` availability as a per-day check, not an assumption.

## Enabling Guidance

### Wait Model

`cursor agent -p` stays up until the agent turn ends (same wait model as `claude -p`). Set wrapper timeouts generously and wait for exit; do not poll.

### Login Recovery

The browser challenge requires the `cursor agent login` process to stay alive to receive the callback. If the waiting process is killed, the browser succeeds but tokens are never written. Run it detached (`nohup cursor agent login ... &`) or interactively in a terminal you control, then verify with `cursor agent about`.

Stale tokens (months old in Keychain) produce `Authentication required` even when `status` shows a cached success line; a fresh `login` rewrites both Keychain entries.

## Known Traps

| Trigger | Failure Mode | Remedy |
|---|---|---|
| Running `cursor -p "..."` without `agent` | Opens the IDE instead of running headless | Always use `cursor agent -p` |
| Assuming IDE login covers the CLI | CLI has separate Keychain tokens; `Authentication required` | `cursor agent login` from the CLI itself |
| Killing the login waiter process | Browser auth succeeds but no callback lands; tokens stay stale | Keep login process alive (nohup or own terminal) |
| Reading exit code alone | Auth/model errors can exit 0 in piped contexts | Check stdout for error text or JSON `is_error` |
| Requesting `gemini-3.7-flash-high-fast` | Model does not exist; error lists all models | Use `-low/-medium/-high` suffixes for Gemini Flash |
| Assuming `-fast` always available | Relay connection failures on `-fast` routes (observed 2026-08-18) | Fallback to base model ID; retry another day |
| Invoking `agent` binary directly | That is Grok Build, not Cursor | Explicitly call `cursor agent` |

## Official References

- https://cursor.com/cli
- https://docs.cursor.com/cli/overview
