# Antigravity CLI

## Metadata

- **Type**: Tool / Focused Skill
- **Target**: Headless `agy --print` invocations
- **Verified Version**: Antigravity CLI **1.1.13**
- **Disambiguation**: `agy-ide` is the IDE launcher; `agy-ide chat` opens the GUI. Automation uses the `agy` binary.

## Goal & Boundaries

### Goal

Utilize an Antigravity subscription to execute a Gemini (or other listed) agent headlessly, write a concrete result file to disk, and capture verifiable audit streams (stdout, stderr, event logs).

### When to Load

Load this file when the user asks for Antigravity / `agy`, or when the root skill router selects it as the Gemini subscription path.

### Boundaries & Authentication

- **Authentication Channel**: `agy` authenticates via Antigravity subscription credentials stored in the system keyring. It does not read `GEMINI_API_KEY`. If `agy models` fails to list models, sign in via the Antigravity desktop application. Do not fall back to `GEMINI_API_KEY` (that routes to a distinct API billing path).
- **Subcommand Boundaries**: 1.1.13 has no `agy login` subcommand. There is no `agy run` subcommand; `--print` / `-p` is a top-level flag.

## Acceptance Criteria

Execution is complete and successful only when all four conditions are satisfied:

1. **Exit Code**: Process terminates with code 0.
2. **Artifact Materialization**: The designated result file exists on disk and is non-empty.
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
  --model "gemini-3.7-flash-high" \
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
| `--model` | Target model id. Always specify explicitly. Skill default: `gemini-3.7-flash-high`. |
| `--mode` | Operational mode: `accept-edits` or `plan`. |
| `--sandbox` | Restrict terminal command capabilities. |
| `--dangerously-skip-permissions` | Auto-approve tool requests. Restrict usage to small trusted scratch directories, only in combination with `--sandbox`, and ensure prompt strictly limits write scope. |
| `--print-timeout` | Internal execution timeout (defaults to **5m** on 1.1.13). Set explicitly; keep outer wrapper timeout higher so logs can flush. |
| `--log-file` | Path for timestamped JSON/event logs. |
| `--output-format` | `text` (default), `json`, `stream-json` (introduced in 1.1.13). |
| `--json-schema` | Constrain final structured output; applies to final item in `stream-json`. |
| `--effort` | Reasoning effort: `low`, `medium`, `high`. |
| `--add-dir` | Add extra accessible workspace directory. |
| `-c` / `--continue` | Continue the most recent conversation. |
| `--conversation` | Resume a conversation by ID. Omit `--continue`/`--conversation` for a fresh session. |

> [!NOTE]
> Headless `--print` runs inherit persistent policies from `settings.json`. Review global and project AGY settings before production execution.

### Available Models (1.1.13)

Verified model list via `agy models`:
- `gemini-3.7-flash-high` (default), `gemini-3.7-flash-medium`, `gemini-3.7-flash-low`
- `gemini-3.6-flash-*`, `gemini-3.5-flash-*`
- `gemini-3.1-pro-high`, `gemini-3.1-pro-low`
- `claude-sonnet-4-6`, `claude-opus-4-6-thinking`
- `gpt-oss-120b-medium`

Supplying an invalid model name causes immediate non-zero exit and prints the available model list. Do not attempt silent fallbacks.

## Known Traps

| Trigger | Failure Mode | Remedy |
|---|---|---|
| Running `agy run ...` | Enters unintended interactive flow; may block waiting for `/dev/tty` | Use top-level flag `agy --print` |
| Assuming no JSON output mode exists | Stale assumption relative to 1.1.13 capabilities | Use `--output-format json` or `stream-json` as needed, but retain result file verification |
| Relying on default 5m `--print-timeout` | Extended generation tasks abort mid-execution | Explicitly pass `--print-timeout` (e.g., `10m`) |
| Invoking inside a large private repository | Sensitive sibling files leak into model context | Isolate execution inside a minimal scratch workspace |
| Attempting `agy-ide chat` as headless fallback | Launches interactive GUI interface | Use CLI binary `agy --print` |

## Official References

- https://github.com/google-antigravity/antigravity-cli
- https://antigravity.google/product/antigravity-cli
- https://antigravity.google/docs/cli-overview
