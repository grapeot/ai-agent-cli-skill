# Antigravity CLI

## Metadata

- **Type**: Tool / Focused Skill
- **Target**: Headless `agy --print` invocations
- **Verified Version**: Antigravity CLI **1.3.5** (verified 2026-10-14 against `agy --help`, `agy models`, and live one-shot runs)
- **Disambiguation**: `agy-ide` is the IDE launcher; `agy-ide chat` opens the GUI. Automation uses the `agy` binary.

## Goal & Boundaries

### Goal

Utilize an Antigravity subscription to execute a Gemini (or other listed) agent headlessly, write a concrete result file to disk, and capture verifiable audit streams (stdout, stderr, event logs).

### When to Load

Load this file when the user asks for Antigravity / `agy`, or when the root skill router selects it as the Gemini subscription path.

### Boundaries & Authentication

- **Authentication Channel**: `agy` authenticates via Antigravity subscription credentials stored in the system keyring. It does not read `GEMINI_API_KEY`. If `agy models` fails to list models, sign in via the Antigravity desktop application. Do not fall back to `GEMINI_API_KEY` (that routes to a distinct API billing path).
- **Subcommand Boundaries**: 1.3.5 has no `agy login` subcommand. There is no `agy run` subcommand; `--print` / `-p` is a top-level flag.

## Acceptance Criteria

Execution is complete and successful only when all four conditions are satisfied:

1. **Exit Code**: Process terminates with code 0.
2. **Artifact Materialization**: The designated result file exists at the intended path on disk and is non-empty. A file appearing somewhere else (e.g., a previous task's scratch directory) is a failed run even with exit code 0.
3. **Hard Checks**: The result file passes all task-specific constraints and validation checks.
4. **Clean Error Stream**: stderr contains no unhandled error. (Startup log messages indicating an initial unauthenticated state followed by `silent auth succeeded` are expected and do not indicate failure if exit code is 0).

> [!IMPORTANT]
> Stdout serves only as an execution summary note; do not treat stdout content as the primary product.

## Available Resources & CLI Reference

### Installation & Binary Verification

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

On managed environments, prefer downloading pinned release assets with published SHA-256 hashes from: https://github.com/google-antigravity/antigravity-cli/releases

### Command Shape

```bash
agy --print \
  "Read the complete task from /absolute/path/to/prompt.md and follow it exactly." \
  --model "gemini-3.8-flash-high" \
  --mode accept-edits \
  --sandbox \
  --dangerously-skip-permissions \
  --print-timeout 10m \
  --log-file "/absolute/path/to/events.log" \
  > "/absolute/path/to/stdout.txt" \
  2> "/absolute/path/to/stderr.txt"
```

### Defaults & Key Flags

| Flag | Description & Operational Boundary |
|---|---|
| `--print` / `-p` | Headless execution for a single prompt. |
| `--model` | Target model id. Always specify explicitly. Skill default: `gemini-3.8-flash-high`. |
| `--mode` | Operational mode: `accept-edits`, `auto`, or `plan`. |
| `--sandbox` | Restrict terminal command capabilities. |
| `--dangerously-skip-permissions` | Auto-approve tool requests. Restrict usage to small trusted scratch directories, only in combination with `--sandbox`, and ensure prompt strictly limits write scope. |
| `--print-timeout` | Internal execution timeout; defaults to **0** (`0s`, wait until the turn completes). Set explicitly (e.g. `10m`) so a stuck turn cannot hang forever; keep the outer wrapper timeout higher so logs can flush. |
| `--log-file` | Path for timestamped JSON/event logs. |
| `--output-format` | `text` (default), `json`, `stream-json`. With `json`, stdout is a single object: `{"conversation_id", "status": "SUCCESS", "response", "duration_seconds", "num_turns", "usage": {...}}`. Still verify the result file on disk; `status` alone does not prove the artifact landed in the intended directory. |
| `--json-schema` | Constrain final structured output; applies to final item in `stream-json`. |
| `--effort` | Reasoning effort: `low`, `medium`, `high`, `xhigh`, `max`. |
| `--add-dir` | Add extra accessible workspace directory. |
| `-c` / `--continue` | Continue the most recent conversation. Omit for one-shot tasks. |
| `--conversation` | Resume a previous conversation by ID. Omit for one-shot tasks. |
| `--project` | Pin the session to a specific project ID or name. When omitted (and `--new-project` is not set), `agy` uses `default-cli-project` (`CLI Project`) and scopes workspace access to the current working directory. |
| `--new-project` | Create a persistent project entry in `~/.gemini/config/projects/<uuid>.json`. **Do not use for routine one-shot `--print` runs**: `~/.gemini/config/projects/` is shared with the Antigravity desktop application while CLI conversations live in `~/.gemini/antigravity-cli/`, so `--new-project` floods the desktop UI with empty projects. |

1.3.5 additionally exposes `--prompt` (alias of `--print`), `--agent`, `--disable-slash-commands`, `-i` / `--prompt-interactive`, `--input-format` (NDJSON stdin for `stream-json`), and `--remote-control`, plus the `mic-serve` subcommand. None of these are needed for the standard one-shot `--print` contract above.

> [!NOTE]
> Headless `--print` runs inherit persistent policies from `settings.json`. Review global and project AGY settings before production execution.

### Available Models (1.3.5)

Verified model list via `agy models`:
- `gemini-3.8-flash-high` (skill default), `gemini-3.8-flash-medium`, `gemini-3.8-flash-low`
- `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`
- `claude-opus-5-5-high`, `claude-opus-5-5-medium`, `claude-opus-5-5-low`
- `claude-sonnet-5-5-high`, `claude-sonnet-5-5-medium`, `claude-sonnet-5-5-low`
- `gpt-oss-120b-medium`

Supplying an invalid model name causes immediate non-zero exit and prints the available model list. Do not attempt silent fallbacks.

## Known Traps

| Trigger | Failure Mode | Remedy |
|---|---|---|
| Running `agy run ...` | Enters unintended interactive flow; may block waiting for `/dev/tty` | Use top-level flag `agy --print` |
| Assuming no JSON output mode exists | Stale assumption relative to 1.1.13+ capabilities | Use `--output-format json` or `stream-json` as needed, but retain result file verification |
| Relying on the default `--print-timeout` | Defaults to `0` (`0s`, wait until the turn completes): a stuck turn hangs forever instead of aborting mid-run | Explicitly pass `--print-timeout` (e.g., `10m`) and keep the wrapper timeout higher |
| Invoking inside a large private repository | Sensitive sibling files leak into model context | Isolate execution inside a minimal scratch workspace |
| Passing `--new-project` on every one-shot `--print` run | Creates a permanent `<uuid>.json` in `~/.gemini/config/projects/` per run; because the desktop app shares that directory while CLI conversations stay in `~/.gemini/antigravity-cli/`, thousands of empty projects accumulate in the desktop UI | Omit `--new-project` (and omit `-c`/`--continue`/`--conversation`) so one-shot runs create fresh conversations under `default-cli-project`; set `cwd` to the scratch directory and use absolute paths for both `prompt.md` and the output artifact |
| Using relative paths in the driver prompt | If a project config binds another folder or `cwd` was not switched to the scratch directory, relative paths can resolve against the wrong directory and exit 0 | `cd` into the isolated scratch directory before invoking `agy --print`, use absolute paths in both the driver prompt and `prompt.md`, and verify the artifact materialized at the intended path |
| Attempting `agy-ide chat` as headless fallback | Launches interactive GUI interface | Use CLI binary `agy --print` |

## Official References

- https://github.com/google-antigravity/antigravity-cli
- https://antigravity.google/product/antigravity-cli
- https://antigravity.google/docs/cli-overview
