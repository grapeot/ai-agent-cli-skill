# Antigravity CLI

Headless `agy --print` invocations. Verified against Antigravity CLI **1.1.13**.

`agy-ide` is the IDE launcher. `agy-ide chat` opens the GUI. Automation uses `agy`.

## Goal

Use an Antigravity subscription to run a Gemini (or other listed) agent, write a result file, and leave stdout/stderr/logs that can be audited.

## When to load this file

The user asked for Antigravity / `agy`, or the root skill selected it as the Gemini-subscription path.

## Install

```bash
if ! command -v agy >/dev/null 2>&1; then
  installer="$(mktemp)"
  curl -fsSL https://antigravity.google/cli/install.sh -o "$installer"
  # Review the script, then:
  bash "$installer"
  rm -f "$installer"
fi
agy --version
agy models
```

On a managed machine, prefer a pinned GitHub release asset and its published SHA-256: https://github.com/google-antigravity/antigravity-cli/releases

`agy` uses the Antigravity subscription and the system keyring. It does not read `GEMINI_API_KEY`. If `agy models` cannot list models, sign in through the Antigravity app first. Do not fall back to `GEMINI_API_KEY`; that is a different billing path.

1.1.13 has no `agy login` subcommand.

## Command shape

There is no `agy run`. `--print` / `-p` is a top-level flag.

```bash
agy --print \
  "Read the complete task from /absolute/path/to/prompt.md and follow it exactly." \
  --model "gemini-3.7-flash-high" \
  --mode accept-edits \
  --sandbox \
  --dangerously-skip-permissions \
  --print-timeout 10m \
  --log-file "/absolute/path/to/events.log" \
  > "/absolute/path/to/stdout.txt" \
  2> "/absolute/path/to/stderr.txt"
```

`--dangerously-skip-permissions` is only for a small trusted scratch directory and only together with `--sandbox`. The prompt must name the single result path and forbid other writes.

`--print-timeout` defaults to **5m** on 1.1.13. Set it explicitly. Keep an outer process timeout a few seconds higher so logs can flush.

Headless `--print` still inherits persistent `settings.json` policy. Review global and project AGY settings before a production call.

## Defaults that matter

| Flag | Use |
|---|---|
| `--print` / `-p` | Headless single prompt |
| `--model` | Always pass it. Default in this skill: `gemini-3.7-flash-high` |
| `--mode` | `accept-edits` or `plan` |
| `--sandbox` | Restrict the terminal |
| `--dangerously-skip-permissions` | Auto-approve tool requests |
| `--print-timeout` | Internal wait; default 5m |
| `--log-file` | Timestamped event log |
| `--output-format` | `text` (default), `json`, `stream-json` — added by 1.1.13 |
| `--json-schema` | Structured final result; with `stream-json` it applies to the final item |
| `--effort` | `low`, `medium`, `high` |
| `--add-dir` | Extra workspace directory |
| `-c` / `--continue` | Continue the most recent conversation |
| `--conversation` | Resume by id |

A call without `--continue` / `--conversation` is a fresh conversation.

## Models (1.1.13)

`agy models` listed:

- `gemini-3.7-flash-high` / `medium` / `low` — default high
- `gemini-3.6-flash-*`, `gemini-3.5-flash-*`
- `gemini-3.1-pro-high`, `gemini-3.1-pro-low`
- `claude-sonnet-4-6`, `claude-opus-4-6-thinking`
- `gpt-oss-120b-medium`

An invalid model name exits non-zero and prints the list. Do not silently fall back.

## Completion check

All of:

1. Exit code 0
2. Result file exists and is non-empty
3. Result file satisfies the task's hard checks
4. stderr has no unhandled error

Stdout is a completion note. Do not use it as the product.

Startup logs may say the user is not logged in and then `silent auth succeeded`. That is not a failure if the process later exits 0.

## Known traps

| Trap | What happens | What to do |
|---|---|---|
| `agy run ...` | Wrong interactive path; may hang on `/dev/tty` | Use top-level `agy --print` |
| Assuming there is no JSON mode | Stale relative to 1.1.13 | `--output-format json` / `stream-json` exist; still keep a result file |
| Trusting default 5m timeout | Long writes die mid-run | Pass `--print-timeout` |
| Starting in a large private tree | Secrets enter model context | Use a minimal scratch workspace |
| Treating `agy-ide chat` as fallback | Opens a GUI | Not a headless completion |

## Official docs

- https://github.com/google-antigravity/antigravity-cli
- https://antigravity.google/product/antigravity-cli
- https://antigravity.google/docs/cli-overview
