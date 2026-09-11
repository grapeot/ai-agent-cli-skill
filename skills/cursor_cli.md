# Cursor Agent CLI

## Metadata

- **Type**: Tool / Focused Skill
- **Target**: Non-interactive `cursor agent` invocations
- **Verified Version**: Cursor launcher **3.19.7** / agent CLI **2026.09.08-6caf4ff**, verified on **2026-09-10**
- **Disambiguation**: This is Cursor's agent CLI, reached through the `cursor` launcher's `agent` subcommand. It is not the standalone `~/.local/bin/agent` binary (that one is Grok Build), and it is not the IDE itself.

## Goal & Boundaries

### Goal

Execute a Cursor agent turn non-interactively from a prompt, capture text or JSON output, and ensure the agent persists verified result artifacts to disk.

### When to Load

Load the [ai-agent-cli root skill](./skill_ai_agent_cli.md) first, then this focused file when the user requests Cursor / `cursor agent` CLI or the router selects it. Task-specific stages, input isolation and timeout budgets belong in the calling workflow, not this CLI reference.

### Boundaries & Authentication

- **Entry point**: `cursor agent -p` (the `-p` / `--print` flag is the headless entry; there is no `cursor exec`). The top-level `cursor` binary without `agent` just opens the IDE.
- **Authentication**: `cursor agent login` (browser challenge) or `CURSOR_API_KEY` / `--api-key`. These are authentication options; do not infer a separate billing path from the flag alone. Check state with `cursor agent status`, `cursor agent about`, `cursor agent --list-models`.
- **Token storage**: macOS Keychain entries `cursor-access-token` / `cursor-refresh-token`. IDE login state (SQLite under `~/Library/Application Support/Cursor`) is **not** shared with the CLI; the CLI has its own tokens.
- **Sessions**: CLI chat IDs are for the CLI. Do not assume an IDE Composer thread and a headless `--resume` ID are interchangeable.

## Acceptance Criteria

A Cursor execution is complete and valid only when:

1. **Exit Status**: Process exits with code 0. Note: some auth and model errors also exit 0 — always also check stdout content or the error line.
2. **Artifact Verification**: If a result file was required, it exists at the requested path, is non-empty, and has been read back against the task requirements. A fluent stdout summary is not a substitute.
3. **JSON Conformance**: With `--output-format json`, stdout is parseable JSON with `type: "result"`, `subtype: "success"`, and `is_error: false`. The `session_id` field is the handle for later `--resume`.
4. **Identity**: `cursor agent about` shows the expected account tier before batch runs.

## Available Resources & CLI Reference

### Identity Check

```bash
cursor --version            # launcher version (3.19.7)
cursor agent about          # CLI version, account, default model
cursor agent --list-models  # model IDs available to this account
```

`cursor agent models` is the same model list as `--list-models`.

### Command Shapes

Single-turn with file task (preferred):

```bash
cursor agent -p "Read the complete task from /absolute/path/to/prompt.md and follow it exactly." \
  --model gemini-3.8-flash-high \
  --trust \
  --workspace /absolute/path/to/scratch \
  --output-format json \
  > /absolute/path/to/scratch/stdout.json \
  2> /absolute/path/to/scratch/stderr.log
```

Start the process from the scratch directory too. The prompt file must name the output artifact and its requirements; argv only points to that task file. Capture stdout and stderr separately and apply all acceptance checks above. Use `text` only when structured status is not needed.

Structured output:

```bash
cursor agent -p "..." --output-format json
# -> {"type":"result","subtype":"success","is_error":false,
#     "duration_ms":1234,"result":"...","session_id":"<uuid>"}
```

Headless resume / follow-up (there is no `append` subcommand; `--resume` plus a new prompt is the next turn):

```bash
chat_id=$(cursor agent create-chat)
cursor agent --resume "$chat_id" -p --trust --output-format json \
  "Read the complete task from /absolute/path/to/prompt.md and follow it exactly."
cursor agent --resume "$chat_id" -p --trust --output-format json \
  "Continue from the previous turn. Read /absolute/path/to/followup.md and follow it."
```

A first `-p` JSON result already includes `session_id`; `create-chat` is optional when you need the ID before the first turn. `--continue` resumes the most recent CLI session without naming an ID. Independent turns omit both `--resume` and `--continue`; a new process alone does not imply a new conversation when either flag is present.

### Key Flags

| Flag | Description & Operational Boundary |
|---|---|
| `-p` / `--print` | Headless single-turn entry; full tool access including write and shell. Each invocation is a new process: load history if resuming, run one turn, exit. |
| `--output-format` | `text` (default), `json`, `stream-json`; `--stream-partial-output` for deltas (stream-json only). |
| `--mode` / `--plan` | `plan` = read-only planning; `ask` = Q&A read-only. |
| `--model` | Model ID from `--list-models`, or a quoted parameterized ID such as `'claude-opus-4-8[context=1m,effort=high,fast=false]'`. Always pass explicitly. |
| `--trust` | Trust the workspace without prompting (print mode only). Required for smooth headless runs. |
| `--sandbox` | `enabled` / `disabled`; overrides config. |
| `-f` / `--force` / `--yolo` | Auto-approve commands unless explicitly denied. |
| `--approve-mcps` | Auto-approve MCP servers (headless). |
| `--auto-review` | Server classifier auto-runs safe tool calls and prompts for the rest. |
| `--workspace` | Working directory (defaults to cwd). |
| `--add-dir <path>` | Extra workspace root; repeatable. |
| `-w` / `--worktree [name]` | Isolated git worktree at `~/.cursor/worktrees/...`; `--worktree-base` picks the base ref; `--skip-worktree-setup` skips `.cursor/worktrees.json` scripts. |
| `--resume [chatId]` / `--continue` | Resume a CLI chat and send the argv prompt as the next turn. |
| `--api-key` / `CURSOR_API_KEY` | API-key authentication; billing terms must be checked separately. |

`cursor agent ls` and `cursor agent resume` (no ID) are interactive TUI entry points. `ls` needs a real TTY / raw mode and is not a scriptable chat listing. Use `create-chat`, a captured `session_id`, or `--continue` in automation.

Other subcommands exist but are out of scope for a normal `-p` turn: `mcp`, `plugin`, `worker`, `bedrock`, `update`, `install-shell-integration`, `generate-rule`, `logout`.

### Models (verified 2026-09-10, Ultra tier)

Account-dependent. Representative IDs from `--list-models`:

- `auto` (listed default)
- `composer-2.5`, `composer-2.5-fast`
- `gemini-3.8-flash-high`, `gemini-3.8-flash-medium`, `gemini-3.8-flash-low`
- `gemini-3.7-flash-high`, `gemini-3.7-flash-medium`, `gemini-3.7-flash-low`
- Claude family `claude-opus-5-*` / `claude-opus-4-8-*` / `claude-sonnet-5-*` / `claude-fable-5-*`
- GPT family `gpt-5.6-*` / `gpt-5.5-*` / `gpt-5.3-codex-*`
- `cursor-grok-4.6-*`, `cursor-grok-4.5-*`, `kimi-k3-*`, `glm-5.2-*`

The default model for this skill is `gemini-3.8-flash-high` unless the caller specifies another. Re-run `--list-models` before batch jobs and pass `--model` explicitly. IDs and the account default move; `auto` in the model menu does not override the explicit choice.

### Fast is not a `--fast` flag

There is still no `--fast` flag. Speed is selected in two ways:

1. **Suffix IDs** from `--list-models`: `composer-2.5` vs `composer-2.5-fast`, `cursor-grok-4.6-high` vs `cursor-grok-4.6-high-fast`.
2. **Bracket overrides** on `--model`: `'claude-opus-4-8[context=1m,effort=high,fast=false]'`. Quote the whole token so the shell does not split on `[` / `]`.

Gemini 3.8 Flash still has no `-fast` ID. Its effort levels are `-low` / `-medium` / `-high`. Requesting `gemini-3.8-flash-high-fast` fails with the available-model list.

`-fast` routes can fail independently of the base model. On 2026-08-18, `composer-2.5-fast` and `cursor-grok-4.6-medium-fast` hit relay connection retries (`agentn.global.api5.cursor.sh`) while base IDs on the same account worked. Probe with `--list-models` and one cheap `-p` call before relying on Fast.

## Enabling Guidance

### Wait Model

`cursor agent -p` stays up until the agent turn ends (same wait model as `claude -p`). There is no `--print-timeout` flag in the verified CLI. The parent process owns timeout enforcement; use the calling task's budget and wait for exit.

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
| Using `cursor agent ls` in a script | Ink TUI; fails without raw-mode stdin | Capture `session_id` from JSON or call `create-chat` |
| Assuming IDE chats resume via `--resume` | CLI and IDE threads are not a documented shared pool | Resume only CLI `session_id` values |
| Requesting `gemini-3.8-flash-high-fast` | Model does not exist; error lists all models | Use `-low/-medium/-high` suffixes for Gemini Flash |
| Assuming `-fast` always available | Relay connection failures on `-fast` routes (observed 2026-08-18) | Fallback to base model ID or `[fast=false]`; retry another day |
| Invoking `agent` binary directly | That is Grok Build, not Cursor | Explicitly call `cursor agent` |

## Official References

- https://cursor.com/cli
- https://cursor.com/docs/cli/overview
- https://cursor.com/docs/cli/headless
- https://cursor.com/docs/cli/reference/output-format
