# Claude Code CLI

## Metadata

- **Type**: Tool / Focused Skill
- **Target**: One-shot `claude` calls, SDK-hosted working sessions, and existing-session control
- **Verified Version**: CLI help rechecked on **2.1.299** (2026-10-14); live session, Remote Control, and auto mode experiments verified with CLI **2.1.299** and Agent SDK **0.3.299** on macOS. Earlier one-shot baseline: **2.1.220**. Model aliases and untested providers are not newly certified by these experiments.
- **Disambiguation**: `Claude Code` refers specifically to Anthropic's `claude` CLI binary. A model subagent whose backend model happens to be Claude is not Claude Code.

## Goal & Boundaries

### Goal

Execute coding tasks in the intended Claude Code environment, or interact with an active conversation without accidentally creating a duplicate process or session fork. Verify task artifacts and correlated conversation events rather than relying on unverified wrapper summaries.

### When to Load

Load this file when a task explicitly calls for Claude Code, or when the root skill router selects `claude`.

### Select the Operation

| Intent | Recommended Interface & Acceptance Gate |
|---|---|
| Independent one-shot task | `claude -p`; wait for process exit and verify the requested result file |
| Program-owned multi-turn session | Agent SDK or bidirectional `stream-json`; keep host alive and consume stream |
| Discover or message an active local session | Run `claude agents --json`, look up exact registry, deliver via peer inbox; do not resume an active process |
| Remote list, history, stream, or interrupt | Code cloud session ID and controller HTTP protocol; distinguish official CLI support from internal APIs |
| Resume a stopped conversation | Explicit local session ID (`-r` or SDK `resume`), followed by identity verification; this is lifecycle management, not live append |

For any live-session, Remote Control, normal-tools auto mode, or existing-object operation, load [Claude session control](./references/claude_sessions.md). That file is a repository-local internal reference, not an additional globally exposed skill.

## Acceptance Criteria

### One-Shot Invocations

A one-shot command execution is complete when all applicable checks pass:

- **Exit Status**: Process terminates cleanly with exit code 0.
- **Artifact Verification**: When a result file is requested, the file exists, is non-empty, and satisfies all hard task requirements (such as schema, required tokens, or expected paths). For conversational queries without a requested file deliverable, verify the actual returned response.
- **Schema Validation**: If `--output-format json` is used, stdout is valid, parseable JSON conforming to any specified schema.
- **Execution Auditability**: The invoking wrapper must record the exact command line executed, prompt and result file paths, logs, and evidence of result-file read-back.

### Live Session Operations

For existing or long-running sessions, follow the identity-and-event contract defined in the root skill and the [Claude session reference](./references/claude_sessions.md). Do not require a live worker to exit, and do not invent artificial file deliverables for conversational interactions.

## Available Resources & CLI Reference

### Command Shapes

Standard headless invocation using a prompt file:

```bash
claude -p --model opus \
  --permission-mode acceptEdits \
  --tools Read,Edit,Write \
  --output-format json \
  "Read /path/to/prompt.md and follow it exactly."
```

Driver prompt via stdin:

```bash
printf '%s' "$driver_prompt" | claude -p --model opus --permission-mode acceptEdits
```

Keep driver prompts short. Put detailed tasks, constraints, and schemas into a dedicated prompt file.

### Key Flags & Defaults

| Flag | Purpose & Operational Boundary |
|---|---|
| `-p` / `--print` | Headless execution mode. Skips interactive trust dialogs. Execute only in trusted working directories. |
| `--model` | Model alias or explicit ID. Default recommendation is `opus` unless the caller specifies otherwise. Do not invent unverified aliases. |
| `--output-format` | Output format: `text` (default), `json`, or `stream-json`. |
| `--json-schema` | Enforce a JSON Schema constraint on the final output payload. |
| `--permission-mode` | Modes include `acceptEdits`, `auto`, `bypassPermissions`, `manual`, `dontAsk`, and `plan`. For normal authorized working sessions, prefer the verified `auto` recipe. `auto` is an active evaluation policy, not a bypass or always-allow callback. |
| `--tools` | Built-in tool list (e.g., `Bash,Edit,Read`). `default` preserves built-ins; `""` disables them. Account MCP tools require separate scope verification; see the reference. |
| `--allowed-tools` / `--disallowed-tools` | Fine-grained tool permission rules. |
| `--effort` | Reasoning effort level: `low`, `medium`, `high`, `xhigh`, `max`. Valid on 2.1.220 (retained historical scope). |
| `--add-dir` | Whitelist additional filesystem trees for tool access. |
| `-c` / `--continue` | Continue the most recent conversation in the current working directory. |
| `-r` / `--resume` | Restore a local conversation by ID. Not a general live append interface; running-background send-then-attach has separate TTY-dependent behavior. |
| `--fork-session` | Fork an existing conversation into a new session UUID upon resuming. |
| `--session-id` | Explicitly specify a session UUID. |
| `--no-session-persistence` | Print-mode only. Disables conversation state persistence on disk. |
| `--bare` | Minimal startup mode. Skips keychain/OAuth discovery, automatic `CLAUDE.md` loading, and default peer inbox. Not suitable for native login, normal tools, or Remote Control. |
| `--setting-sources` | Explicitly load settings from `user,project,local` when a working session needs standard workspace configuration. |
| `--bg` / `--background` | Dispatch work in the background. Do not combine with `--resume` on an already-running session to append work, as this can spawn an unintended duplicate conversation. |
| `--remote-control [name]` | Interactive local session with Remote Control enabled. Distinct from the persistent `remote-control` server. |
| `--cloud [target]` | Cloud session creation and follow-up entry point. Detailed bridge boundaries are covered in the reference. |

## Enabling Guidance & Best Practices

### Time Budgeting

Allocate sufficient wall-clock time for multi-turn execution. Budget 10 minutes for drafting or mixed file-editing tasks, and 15 minutes for broad research workflows. Do not constrain autonomous turns with short shell command timeouts (such as 120 seconds).

### Workspace and Session Management

- **Workspace Root**: Start project work in the caller's actual workspace root. Ensure `AGENTS.md` or `CLAUDE.md` and routed instructions are loaded, and preserve requested model and language choices. Whitelist extra directories using `--add-dir`.
- **Session Identity Isolation**: Claude session UUIDs are independent of orchestrator session IDs. Never pass foreign orchestrator UUIDs to `--resume`.
- **Stopped vs. Running Sessions**: Restore stopped conversations using `-c`/`-r` or SDK `resume`. For an active running session, deliver tasks via its local peer inbox or controller rather than restoring its transcript into a competing process.
- **Normal Working SDK Recipe**: For program-owned sessions, use the `claude_code` system prompt preset, `settingSources: ['user', 'project', 'local']`, normal tools, and effective `auto` mode. Verify actual tool outcomes (Bash `pwd`/date, Write probes, Read read-backs) and permission state, rather than assuming launch options alone guarantee correct execution.
- **Remote Details**: Consult the [Claude session reference](./references/claude_sessions.md) before enabling Remote Control, selecting live targets, or interpreting transport receipts.

### Long Calls and Handoffs

- **Responsive Orchestration**: A long autonomous turn should run under a dedicated background worker if the parent orchestrator must stay interactive. Short metadata queries, `--help` inspections, and API reads do not require an intermediate model wrapper.
- **Direct Child Execution**: When an execution worker owns the invocation, it must launch the CLI or SDK directly rather than delegating through another agent layer. An SDK spawning its own Claude child process is executing directly, not nesting an extra research agent.
- **Handoff Fidelity**: Retain the complete user instructions and original feedback in handoff files. Use explicit filesystem paths and verify actual outputs against expectations.

### Research vs. Material Processing

- **Research Workflows**: Provide clear exploration goals, boundaries, and starting points. Ensure `Bash` is included in `--tools`. Avoid pre-filtering and stuffing intermediate findings unless external resources are inaccessible to Claude.
- **Targeted File Transformations**: When evaluating or editing a predetermined set of files, supply those file paths directly. Exclude `Bash` when file-only editing tools (`Read,Edit,Write`) suffice.

## Known Traps

| Trigger | Failure Mode | Remedy |
|---|---|---|
| Calling `claude` directly from an interactive main agent | Parent agent blocks for several minutes | Run the CLI under a background worker process if the orchestrator must remain responsive |
| Nesting another agent layer around `claude` | Timeouts, lost context, and silent hangs | The worker owning the task must invoke `claude` directly without extra intermediate agents |
| Using `--tools Read,Edit,Write` for research tasks | Agent cannot perform discovery or run commands | Include `Bash` in the `--tools` parameter |
| Quoting a multi-paragraph prompt directly on argv | Argument length limits or quote escaping failures | Pass the prompt via stdin or reference an isolated prompt file |
| Relying solely on stdout for file-producing tasks | Output truncation or unwritten edits | Verify the requested result file on disk; for live sessions, correlate event UUIDs and outcomes |
| Using `--bg --resume` to append to an active session | A separate duplicate session copy can be created | Use the running process's peer inbox or controller; reserve `--resume` for stopped sessions |
| Configuring normal work like a no-tools fixture | Agent cannot read system time or inspect files | Load standard presets, settings, and tools; verify effective auto mode and actual tool results |

## Official References

- [Claude Code Headless Mode](https://code.claude.com/docs/en/headless)
- [Claude Agent SDK TypeScript](https://code.claude.com/docs/en/agent-sdk/typescript)
- [Cross-Session Messaging](https://code.claude.com/docs/en/cross-session-messaging)
- [Remote Control](https://code.claude.com/docs/en/remote-control)
