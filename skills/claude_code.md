# Claude Code CLI

## Metadata

- **Type**: Tool / Focused Skill
- **Target**: Non-interactive `claude` invocations
- **Verified Version**: Claude Code **2.1.220**
- **Disambiguation**: `Claude Code` is the `claude` CLI. A subagent whose backend model happens to be Claude is not Claude Code.

## Goal & Boundaries

### Goal

Run a complete file-aware task with `claude -p` and produce verifiable disk artifacts without relying on or trusting the wrapper's summary.

### When to Load

Load this file when the user asks for Claude Code, or when the root skill router selects `claude`.

## Acceptance Criteria

A task execution is considered complete only when all of the following pass:

- **Exit Status**: Process exits with code 0.
- **Artifact Verification**: If a result file was required, it exists, is non-empty, and satisfies the task's hard checks.
- **Schema Validation**: If `--output-format json` was specified, stdout is valid, parseable JSON.
- **Auditability**: The wrapper can produce the exact command line that ran.

## Available Resources & CLI Reference

### Command Shape

Standard headless invocation:

```bash
claude -p --model opus \
  --permission-mode acceptEdits \
  --tools Read,Edit,Write \
  --output-format json \
  "Read /absolute/path/to/prompt.md and follow it exactly."
```

Driver prompt via stdin:

```bash
printf '%s' "$driver_prompt" | claude -p --model opus --permission-mode acceptEdits
```

Long prompts go on stdin or, better, live in a file named by the driver prompt.

### Defaults & Key Flags

| Flag | Description & Operational Boundary |
|---|---|
| `-p` / `--print` | Required for headless execution. Skips workspace trust dialog. Run only in trusted directories. |
| `--model` | Alias (`opus`, `sonnet`, `fable`) or a full model id. Skill default is `opus` unless specified otherwise. |
| `--output-format` | `text` (default), `json`, `stream-json`. |
| `--json-schema` | Constrain the final JSON payload. |
| `--permission-mode` | `acceptEdits` for file modifications. Also: `auto`, `bypassPermissions`, `manual`, `dontAsk`, `plan`. |
| `--tools` | Built-in allow list (e.g., `Bash,Edit,Read`). `default` preserves all tools; `""` disables tools. |
| `--allowed-tools` / `--disallowed-tools` | Additional tool allow/deny rules. |
| `--effort` | Reasoning effort: `low`, `medium`, `high`, `xhigh`, `max`. Valid on 2.1.220 (do not treat as removed). |
| `--add-dir` | Additional workspace directories tools may touch. |
| `-c` / `--continue` | Continue the most recent conversation in this directory. |
| `-r` / `--resume` | Resume by session id. |
| `--fork-session` | Resume into a new session id. |
| `--session-id` | Set the session UUID. |
| `--no-session-persistence` | Print-mode only; disables session persistence so session cannot be resumed. |
| `--bare` | Skip hooks, plugins, `CLAUDE.md` discovery, and keychain reads. |

## Enabling Guidance & Best Practices

### Time Budgeting

Budget 10 minutes for drafting or mixed research+write tasks, and 15 minutes for heavy research. This operates on a minute-scale timeframe, not as a brief 120s shell command.

### Session Management

- Claude Code sessions are independent of the parent orchestrator's sessions. Resume only via `claude -c` or `claude -r`. Do not supply a parent orchestrator session ID to `--resume`.
- Use session resume for multi-turn continuations of an existing Claude Code conversation; omit it for fresh one-shot invocations.

### Research vs. Material Processing

- **Research Tasks**: Provide a high-level goal, boundaries, starting paths, and ensure `Bash` is included in `--tools`. Avoid pre-searching and stuffing findings as the exclusive corpus unless sources are inaccessible to Claude.
- **Evaluation Tasks**: If the objective is "judge this known set of files", supply those files directly without unnecessary bash tooling. File-only edits should omit `Bash`.

## Known Traps

| Trigger | Failure Mode | Remedy |
|---|---|---|
| Calling `claude` directly from main interactive agent | Parent agent blocks for minutes | Wrap call in a background worker process if parent must remain responsive |
| Nesting another agent layer around `claude` | Timeouts and silent hangs occur | Worker launching `claude` must execute it directly, not dispatch another intermediate agent |
| Using `--tools Read,Edit,Write` on a research job | Agent cannot perform retrieval or exploration | Include `Bash` in the `--tools` list |
| Quoting a long prompt on argv | Shell character limits or quoting corruption | Supply prompt via stdin or reference an isolated prompt file |
| Treating stdout as the primary product | Output truncation or lost file edits | Require a concrete result file path on disk |

## Official References

- https://docs.anthropic.com
