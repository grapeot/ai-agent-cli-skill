# Claude Code CLI

Non-interactive `claude` invocations. Verified against Claude Code **2.1.220**.

`Claude Code` is the `claude` CLI. A subagent whose backend model happens to be Claude is not Claude Code.

## Goal

Run a complete file-aware task with `claude -p` and leave a result that can be checked without trusting the wrapper's summary.

## When to load this file

The user asked for Claude Code, or the root skill selected `claude`.

## Command shape

```bash
claude -p --model opus \
  --permission-mode acceptEdits \
  --tools Read,Edit,Write \
  --output-format json \
  "Read /absolute/path/to/prompt.md and follow it exactly."
```

Long prompts go on stdin or, better, live in a file the driver prompt names.

```bash
printf '%s' "$driver_prompt" | claude -p --model opus --permission-mode acceptEdits
```

Research / retrieval tasks need `Bash` in `--tools`. File-only edits should not.

## Defaults that matter

| Flag | Use |
|---|---|
| `-p` / `--print` | Required for headless. Skips the workspace trust dialog. Only run it in a directory you trust. |
| `--model` | Alias (`opus`, `sonnet`, `fable`) or a full id. This skill's default is `opus` unless the caller names another model. |
| `--output-format` | `text` (default), `json`, `stream-json` |
| `--json-schema` | Constrain the final payload |
| `--permission-mode` | `acceptEdits` for file work. Also: `auto`, `bypassPermissions`, `manual`, `dontAsk`, `plan` |
| `--tools` | Built-in allow list, e.g. `Bash,Edit,Read`. `default` keeps all tools. Empty string disables tools. |
| `--allowed-tools` / `--disallowed-tools` | Extra allow/deny rules |
| `--effort` | `low`, `medium`, `high`, `xhigh`, `max` |
| `--add-dir` | Extra directories the tools may touch |
| `-c` / `--continue` | Continue the most recent conversation in this directory |
| `-r` / `--resume` | Resume by session id |
| `--fork-session` | Resume into a new session id |
| `--session-id` | Set the session UUID |
| `--no-session-persistence` | Print-mode only; the session cannot be resumed |
| `--bare` | Skip hooks, plugins, CLAUDE.md discovery, keychain reads |

`--effort` is valid on 2.1.220. Do not treat it as removed.

## Completion check

- Exit code 0
- If a result file was required: it exists, is non-empty, and passes the task's hard checks
- If `--output-format json` was used: stdout is parseable JSON
- The wrapper can show the command that actually ran

Budget 10 minutes for drafting or mixed research+write, 15 minutes for heavy research. This is a minute-scale job, not a 120s shell command.

## Session resume

Claude Code sessions are not the parent orchestrator's sessions. Resume only with `claude -c` / `claude -r`. Do not feed a parent session id to `--resume`.

Use resume for a multi-turn continuation of the same Claude Code conversation. Skip it for a fresh one-shot.

## Research vs materials

If the task is research, give a goal, bounds, starting paths, and `Bash`. Do not pre-search and stuff the findings in as the only corpus unless the sources are unreachable to Claude.

If the task is "judge this known set of files," give those files.

## Known traps

| Trap | What happens | What to do |
|---|---|---|
| Calling `claude` from the main interactive agent | The parent blocks for minutes | Wrap the call in a background worker if the parent must stay responsive |
| Nesting another agent around `claude` | Timeouts and silent hangs | The worker that launches `claude` should exec it, not dispatch yet another agent |
| `--tools Read,Edit,Write` on a research job | No retrieval | Include `Bash` |
| Quoting a long prompt on argv | Shell corruption | stdin or a prompt file |
| Treating stdout as the product | Truncation, lost edits | Require a result file |

## Official docs

- https://docs.anthropic.com
