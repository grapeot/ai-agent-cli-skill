# OpenCode CLI

Non-interactive `opencode run` and `opencode serve` invocations. Interface taken from the official CLI docs dated **2026-08-16**. Re-run `opencode --help` on the target machine before a production change; this file was not checked against a local binary in the authoring session.

## Goal

Run an OpenCode task headlessly, optionally against an already-running server, and recover a result file (with stdout JSON as fallback).

## When to load this file

The user asked for OpenCode, or the root skill selected `opencode`.

## Command shape

Standalone run is valid:

```bash
opencode run --format json -m "provider/model" \
  --dir "/absolute/path/to/project" \
  "Read /absolute/path/to/project/tmp/prompt.md and write JSON to /absolute/path/to/project/tmp/result.json."
```

Attach to a long-lived server when you want to avoid MCP/server cold start:

```bash
opencode serve --port 4096
opencode run --attach "http://localhost:4096" --format json -m "provider/model" "..."
```

Older notes that `opencode run` always fails with "Session not found" unless a server is already up are stale relative to the 2026-08-16 docs.

## Defaults that matter

| Flag | Use |
|---|---|
| `--attach` | URL of a running `serve` / `web` backend |
| `-m` / `--model` | `provider/model` |
| `--agent` | Agent name (default depends on config) |
| `--dir` | Working directory. When attaching, this is a path on the server |
| `--format` | `json` for raw JSON events |
| `--variant` | Provider-specific reasoning effort (`high`, `max`, `minimal`, …) |
| `--file` / `-f` | Attach files to the message |
| `--continue` / `-c` | Continue the last session |
| `--session` / `-s` | Continue a session id |
| `--fork` | Fork when continuing |
| `--title` | Session title |
| `--auto` | Auto-approve permissions that are not denied |
| `--port` | Local server port for a one-shot run (random if omitted) |
| `--username` / `--password` | Basic auth for a protected server |

`opencode serve` and `opencode web` start the HTTP API. `web` also opens a browser. Set `OPENCODE_SERVER_PASSWORD` to enable basic auth (username defaults to `opencode`).

List models with `opencode models [provider]`.

## Workspace boundary

OpenCode tools are scoped to the server/project directory. Prompt files and result files must live inside that tree. Paths such as `/tmp/prompt.md` are a common failure when the server was started from a project root.

## Completion check

- Exit code 0
- Result file exists and is non-empty
- If the result file is empty: parse `--format json` stdout for a JSON object and treat that as a degraded success only when the schema matches
- Retry a bounded number of times (three is enough) before failing

Do not trust a prose "done" line in stdout.

## Known traps

| Trap | What happens | What to do |
|---|---|---|
| Result path outside the project | Agent cannot write it | Keep I/O under `--dir` |
| Agent prints JSON and skips the file | Empty result file | Extract JSON from stdout, then retry |
| Forwarding unsupported sampling params | Some providers reject the request | Do not send `presence_penalty` / `frequency_penalty` / `stop` unless that model documents them |
| Killing a shared `serve` process | Drops other attached clients | Do not restart a server you did not start |

## Official docs

- https://opencode.ai/docs/cli
- https://opencode.ai/docs/server
