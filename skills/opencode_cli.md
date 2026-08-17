# OpenCode CLI

## Metadata

- **Type**: Tool / Focused Skill
- **Target**: Non-interactive `opencode run` and `opencode serve` invocations
- **Verified Date**: Interface derived from official CLI documentation dated **2026-08-16** (re-run `opencode --help` on target machine before production changes; this file was not verified against a local binary in the authoring session)

## Goal & Boundaries

### Goal

Run an OpenCode task headlessly—either standalone or attached to an existing server—and recover a verified result file (falling back to stdout JSON extraction only when necessary).

### When to Load

Load this file when the user requests OpenCode, or when the root skill router selects `opencode`.

### Workspace & Execution Boundaries

- **Workspace Scoping**: OpenCode tools are strictly scoped to the server/project directory (`--dir`). Prompt files and result destination files must reside within that directory tree. Paths outside the project root (such as `/tmp/prompt.md`) cause file access failures.
- **Provider Parameter Restrictions**: Do not forward unsupported sampling parameters (`presence_penalty`, `frequency_penalty`, `stop`) unless specifically documented by the chosen provider/model, as some providers will reject requests containing unknown parameters.
- **Shared Server Hygiene**: Do not terminate or restart a shared `opencode serve` process started by another caller, as doing so drops all other active client connections.

## Acceptance Criteria

An invocation is considered successful when:

- **Exit Status**: Process exits with code 0.
- **Artifact Verification**: The result file exists on disk and is non-empty. Never trust a mere prose "done" notice in stdout.
- **Degraded Fallback**: If the result file is empty, parse `--format json` stdout for a JSON object and treat it as degraded success only if the extracted object matches the expected schema.
- **Bounded Retries**: Limit retry attempts to a bounded count (three attempts is sufficient) before terminating with failure.

## Available Resources & CLI Reference

### Command Shapes

Standalone execution (valid directly; older notes claiming `opencode run` requires a pre-existing server to prevent "Session not found" errors are obsolete as of 2026-08-16):

```bash
opencode run --format json -m "provider/model" \
  --dir "/absolute/path/to/project" \
  "Read /absolute/path/to/project/tmp/prompt.md and write JSON to /absolute/path/to/project/tmp/result.json."
```

Attach to a persistent server (eliminates MCP/server startup overhead):

```bash
opencode serve --port 4096
opencode run --attach "http://localhost:4096" --format json -m "provider/model" "..."
```

### Defaults & Key Flags

| Flag | Description & Operational Boundary |
|---|---|
| `--attach` | URL of an active `serve` or `web` backend. |
| `-m` / `--model` | Target model in format `provider/model`. |
| `--agent` | Specific agent configuration name (defaults per configuration). |
| `--dir` | Working directory. When attaching to a server, represents path on the server. |
| `--format` | Output format: `json` emits raw JSON events. |
| `--variant` | Provider reasoning effort setting (`high`, `max`, `minimal`, etc.). |
| `--file` / `-f` | Attach files to message context. |
| `--continue` / `-c` | Resume the most recent session. |
| `--session` / `-s` | Resume a session by ID. |
| `--fork` | Fork the session upon continuation. |
| `--title` | Set session title. |
| `--auto` | Automatically approve permissions that are not explicitly denied. |
| `--port` | Local port for one-shot server (assigned randomly if omitted). |
| `--username` / `--password` | Basic authentication credentials for protected servers. |

### Server Management & Model Discovery

- `opencode serve`: Starts the background HTTP API.
- `opencode web`: Starts the HTTP API and opens a web browser.
- Set environment variable `OPENCODE_SERVER_PASSWORD` to enable basic authentication (username defaults to `opencode`).
- Discover available models via: `opencode models [provider]`.

## Known Traps

| Trigger | Failure Mode | Remedy |
|---|---|---|
| Setting result path outside the project directory | Child agent cannot access or write to the path | Ensure all prompt and result file paths reside under `--dir` |
| Agent prints JSON to stdout but skips file write | Result file is missing or empty | Extract JSON from stdout, validate schema, then retry |
| Passing unsupported sampling parameters | Provider API rejects request | Do not send `presence_penalty`, `frequency_penalty`, or `stop` unless documented by model |
| Terminating a shared `opencode serve` process | Drops active connections of other attached clients | Only stop servers initialized by your own wrapper |

## Official References

- https://opencode.ai/docs/cli
- https://opencode.ai/docs/server
