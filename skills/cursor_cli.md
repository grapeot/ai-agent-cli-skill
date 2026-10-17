# Cursor Agent CLI

## Metadata

- **Type**: Tool / Focused Skill
- **Target**: Non-interactive `cursor agent` invocations
- **Verified Version**: Cursor launcher **3.24.18** / agent CLI **2026.10.16-e3cb207**, rechecked on **2026-10-17** (`cursor --version`, `cursor agent --version`, current help, `--list-models` on an eligible paid tier). The isolated read/write probe remains the **2026-10-16** fact on agent CLI **2026.09.18-9a7762b**. It was not repeated on the 2026-10-17 binary.
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

A turn is successful only when the process exits 0 and every required artifact has been read back. For `json` or `stream-json`, also require the last JSON object to have `type: "result"`, `subtype: "success"`, and boolean `is_error: false`. For `text`, inspect the response for auth/model errors rather than requiring a JSON envelope. Auth and model errors can also exit 0. A summary, a started manifest, or a candidate path list is not source validity. A checkpoint can lag disk. Empty redirected shell output does not mean a build or test passed; read the report or log.

`jq`'s `//` treats `false` as absent. This checker keeps the boolean, for one JSON object or for `stream-json` NDJSON:

```bash
jq -s --exit-status '.[-1].type == "result" and .[-1].subtype == "success" and (.[-1].is_error == false)'
```

In the recorded timeout-wrapped runs, exit 124 meant the outer runner's deadline; `RetriableError: WritableIterable is closed` was observed with exit 1. These are observations, not Cursor-wide exit-code guarantees. An unknown exit, including a wrapper that assigned zsh's readonly `status`, is not 124 and is not success. `session_id` from the init event or the result is the `--resume` handle. `cursor agent about` shows the expected account tier before batch runs.

## Available Resources & CLI Reference

### Identity Check

```bash
cursor --version            # launcher version (3.24.18 on 2026-10-17)
cursor agent --version      # agent CLI (2026.10.16-e3cb207 on 2026-10-17)
cursor agent about          # account and default model
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

Verified isolated read/write probe on 2026-10-16. The caller selected this model. The skill default remains `gemini-3.8-flash-high`:

```bash
cursor agent -p "Read the task file and follow it." \
  --model grok-4.7-high-fast \
  --trust \
  --force \
  --workspace /absolute/path/to/scratch \
  --output-format json
```

That probe exited 0. stdout was `type: "result"`, `subtype: "success"`, `is_error: false`. The requested output file existed and was read back. stderr showed one connection-lost/retry sequence, then the same requested model route succeeded. Treat that stderr sequence as recoverable: it is not an automatic fatal failure, and it was not a fallback to another model. The parent applies an outer process timeout. There is no `--print-timeout` flag.

`stream-json` with `--stream-partial-output` exposes partial deltas during the turn. A final-only `json` capture has come back empty after an outer timeout in the 600–1200 second range. Keep the init `session_id` when no result arrives. A `--resume <id>` follow-up continued that same UUID, including after an interrupted turn. Resume that CLI id. `--continue` selects the latest CLI session and does not name an id.

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
| `--trust` | Trust the workspace without prompting. Required for smooth headless runs. |
| `--sandbox` | `enabled` / `disabled`; overrides config. |
| `-f` / `--force` / `--yolo` | Auto-approve commands unless explicitly denied. The 2026-10-16 read/write probe passed `--force` together with `--trust`. `--trust` skips the workspace trust prompt; `--force` skips command approval prompts. |
| `--approve-mcps` | Auto-approve MCP servers (headless). |
| `--auto-review` | Server classifier auto-runs safe tool calls and prompts for the rest. |
| `--workspace` | Working directory (defaults to cwd). |
| `--add-dir <path>` | Extra workspace root; repeatable. |
| `-w` / `--worktree [name]` | Isolated git worktree at `~/.cursor/worktrees/...`; `--worktree-base` picks the base ref; `--skip-worktree-setup` skips `.cursor/worktrees.json` scripts. |
| `--resume [chatId]` / `--continue` | Resume a CLI chat and send the argv prompt as the next turn. |
| `--api-key` / `CURSOR_API_KEY` | API-key authentication; billing terms must be checked separately. |

`cursor agent ls` and `cursor agent resume` (no ID) are interactive TUI entry points. `ls` needs a real TTY / raw mode and is not a scriptable chat listing. Use `create-chat`, a captured `session_id`, or `--continue` in automation.

Other subcommands exist but are out of scope for a normal `-p` turn: `mcp`, `plugin`, `worker`, `bedrock`, `update`, `install-shell-integration`, `generate-rule`, `logout`. `persist` (`list` / `attach` / `stop`) is in current help only as surviving a terminal or SSH disconnect; see Foreground CLI vs host-asynchronous execution.

### Models

Account-dependent. `--list-models` remains authoritative. Representative IDs from the 2026-09-10 Ultra-tier listing, plus Grok 4.7 IDs rechecked on 2026-10-16 for an eligible paid tier:

- `auto` (listed default on 2026-09-10)
- `composer-2.5`, `composer-2.5-fast`
- `gemini-3.8-flash-high`, `gemini-3.8-flash-medium`, `gemini-3.8-flash-low`
- `gemini-3.7-flash-high`, `gemini-3.7-flash-medium`, `gemini-3.7-flash-low`
- Claude family `claude-opus-5-*` / `claude-opus-4-8-*` / `claude-sonnet-5-*` / `claude-fable-5-*`
- GPT family `gpt-5.6-*` / `gpt-5.5-*` / `gpt-5.3-codex-*`
- Grok 4.7, verified 2026-10-16, without the old `cursor-` prefix: `grok-4.7-low`, `grok-4.7-low-fast`, `grok-4.7-medium`, `grok-4.7-medium-fast`, `grok-4.7-high`, `grok-4.7-high-fast`, `grok-4.7-xhigh`, `grok-4.7-xhigh-fast`. The 2026-09-10 listing used `cursor-grok-4.6-*` and `cursor-grok-4.5-*`.
- `kimi-k3-*`, `glm-5.2-*` (2026-09-10 listing)

The default model for this skill remains `gemini-3.8-flash-high` unless the caller specifies another. Keep a caller-requested model, including when a Fast route logs a retry. Re-run `--list-models` before batch jobs and pass `--model` explicitly. IDs and the account default move; `auto` in the model menu does not override the explicit choice. On 2026-10-17 that list still included `grok-4.7-high-fast`.

### Fast is not a `--fast` flag

There is still no `--fast` flag. Speed is selected in two ways:

1. **Suffix IDs** from `--list-models`: `composer-2.5` vs `composer-2.5-fast`, `grok-4.7-high` vs `grok-4.7-high-fast`. Current Grok 4.7 IDs omit the older `cursor-` prefix.
2. **Bracket overrides** on `--model`: `'claude-opus-4-8[context=1m,effort=high,fast=false]'`. Quote the whole token so the shell does not split on `[` / `]`.

Gemini 3.8 Flash still has no `-fast` ID. Its effort levels are `-low` / `-medium` / `-high`. Requesting `gemini-3.8-flash-high-fast` fails with the available-model list.

`-fast` routes can fail independently of the base model. On 2026-08-18, `composer-2.5-fast` and `cursor-grok-4.6-medium-fast` hit relay connection retries (`agentn.global.api5.cursor.sh`) while base IDs on the same account worked. On 2026-10-16, `grok-4.7-high-fast` logged one connection-lost/retry sequence and then completed on that same ID (exit 0, JSON success, artifact read back). A connection retry can reconnect the same invocation. Keep the caller-requested model and Fast route; do not silently replace it. An outer retry starts only after state inspection shows no colliding writer. Probe with `--list-models` and one cheap `-p` call before relying on a new Fast route.

## Enabling Guidance

### Use the stream to supervise, not just archive

Pair Cursor invocations with the root skill's [Before dispatch: progress and recovery](./skill_ai_agent_cli.md#before-dispatch-progress-and-recovery) contract. Passing `--output-format stream-json --stream-partial-output` exposes partial turn activity, but redirecting stdout to an NDJSON file only archives the stream unless the owned job or allowed host mechanism evaluates it.

- **Capture the session handle early**: Record `session_id` from the initial stream event (or mint one beforehand with `cursor agent create-chat`) so an interrupted turn has a deterministic `--resume` target even if no final `result` envelope arrives.
- **Inspect event and tool progression**: Judge progress from completed tool calls, file writes, and failure evidence in the NDJSON stream, not from PID liveness or empty stderr alone. Repeated checks of the same dependency can generate events without advancing the task. Do not assume a universal event schema across vendors or invent Cursor monitoring flags.
- **Detect children that outlive the caller**: A turn can keep checking a child process whose lifetime extends beyond the outer CLI deadline. Do not assume the host timeout reaped every child; it is not a Cursor child-cleanup guarantee.
- **Recover without colliding writers**: On outer timeout or transport failure, preserve the NDJSON log, stderr, git diff, and actual workspace files, then inspect processes owned by this invocation before starting a `--resume` turn or replacement writer.
- **Separate file recovery from invocation success**: A stale `in_progress` manifest is not execution authority, and usable files left behind by a timed-out turn do not make that invocation succeed. Structured-output invocation success still requires exit 0, a final `type: "result"` / `subtype: "success"` / boolean `is_error: false` envelope, and independent artifact readback. The existing text-output acceptance rule remains unchanged.

### Wait Model

`cursor agent -p` is foreground. It stays up until the agent turn ends (same wait model as `claude -p`). There is no `--print-timeout` flag. The parent process applies an outer timeout and waits for exit.

### Foreground CLI vs host-asynchronous execution

The CLI process itself returns when the turn finishes. Host asynchrony is a lightweight wrapper waiting on that foreground process. The wrapper does not redo the heavy work and does not busy-poll. It records logs and the exact exit with `ec=$?` (zsh `status` is readonly; assigning it leaves the exit unknown, and unknown is not 124), validates the actual outputs, and sends completion. The deadline is the outer runner. A `timeout` label on the command is the host utility, not a Cursor flag and not a platform guarantee. Before a new writer starts, inspect only processes this invocation owns. Do not assume the host timeout killed every child.

Exit 124 or `RetriableError: WritableIterable is closed` (exit 1) can leave complete or partial files. The invocation stays failed. Inspect real paths, diffs, and owned processes before a follow-up. Accept recovered code only by independent readback and, when the task required it, a build or tests. Do not repeat an external write blindly.

Small compiler- or test-backed fixes and one-file tasks have finished after a package-sized turn timed out. Split implementation, tests, and review into bounded owners. Write files, checkpoints, and the handoff early. Avoid a full rewrite and a repeat of the same broad retry. This is an observed recovery heuristic, not a latency benchmark and not a maximum-duration claim.

This split was exercised on 2026-10-16 with a background wrapper around the `grok-4.7-high-fast` read/write probe above. The wrapper completed automatically after the CLI exited 0. Later client rounds used the same wrapper shape when a turn timed out and left partial files.

Current help also lists `cursor agent persist` with `list`, `attach`, and `stop`. That help only says sessions survive a terminal or SSH disconnect. Detached lifecycle, headless suitability, and completion callbacks are not verified. `persist` is not a validated async job API. Do not invent flags for it.

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
| `jq` `//` on `is_error` | `false` is treated as absent, so success looks failed | Test `.is_error == false` with the Acceptance Criteria checker |
| Exit 124 or `WritableIterable is closed` | Complete or partial files can exist while the invocation is still failed | Inspect paths, diffs, and owned processes. Accept code only after independent readback |
| Wrapper assigns zsh `status` | Readonly, so the recorded exit is unknown | Capture `ec=$?`. Unknown is not 124 |
| Final-only `json` after a long outer timeout | stdout can be empty while partial progress exists | Use `stream-json` and `--stream-partial-output`. Keep the init `session_id` |
| Using `cursor agent ls` in a script | Ink TUI; fails without raw-mode stdin | Capture `session_id` from JSON or call `create-chat` |
| Assuming IDE chats resume via `--resume` | CLI and IDE threads are not a documented shared pool | `--resume` the CLI `session_id` from the init event or the result. `--continue` names no id |
| Requesting `gemini-3.8-flash-high-fast` | Model does not exist; error lists all models | Use `-low/-medium/-high` suffixes for Gemini Flash |
| Assuming `-fast` always available | Some `-fast` routes failed on 2026-08-18 while base IDs worked. On 2026-10-16, `grok-4.7-high-fast` logged one connection-lost/retry and then succeeded on that same model | Judge process exit, JSON `is_error`, and the artifact. A single retry line is recoverable. Keep the caller-requested model |
| Treating `cursor agent persist` as a headless job API | Help only documents survival across a terminal or SSH disconnect. Detached lifecycle, headless suitability, and completion callbacks are unverified | Keep `-p` in the foreground. Use a host wrapper when the main agent must stay responsive. Do not invent persist flags |
| Invoking `agent` binary directly | That is Grok Build, not Cursor | Explicitly call `cursor agent` |

## Official References

- https://cursor.com/cli
- https://cursor.com/docs/cli/overview
- https://cursor.com/docs/cli/headless
- https://cursor.com/docs/cli/reference/output-format
