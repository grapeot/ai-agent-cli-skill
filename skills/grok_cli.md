# Grok Build CLI

## Metadata

- **Type**: Tool / Focused Skill
- **Target**: Non-interactive `grok` invocations
- **Verified Version**: Grok Build **1.0.4** (`grok 1.0.4 (d846eb93d94d)`), reported by official stable channel on **2026-08-16**
- **Disambiguation**: This is xAI's Grok Build CLI. It is not Groq, and it is not the community `superagent-ai/grok-cli` binary that also names itself `grok`.

## Goal & Boundaries

### Goal

Execute a Grok coding-agent turn non-interactively from a prompt file, capture structured stdout or JSON payloads, and ensure the agent persists verified result artifacts to disk.

### When to Load

Load this file when the user requests Grok / Grok Build / `grok` CLI, or when the root skill router selects it.

### Boundaries & Authentication

- **Binary Naming**: Always execute `grok`, never `agent` (the installer may link `$HOME/.local/bin/agent`, but `agent` is an ambiguous generic name).
- **Authentication Selection**: Authenticate via `grok login` (subscription / OAuth) or `XAI_API_KEY`. Check active status with `grok models`.
- **API Key Precedence**: If `XAI_API_KEY` is present in the environment, version 1.0.4 prioritizes the API key over stored subscription credentials in `~/.grok/auth.json`. Explicitly unset `XAI_API_KEY` to enforce subscription usage.
- **Remote Login Modes**: For headless/SSH systems, use `grok login --device-auth` (alias `--device-code`). Do not combine with `--oauth` (they are mutually exclusive). `--oauth` requires a local browser capable of reaching `127.0.0.1`.

## Acceptance Criteria

A Grok execution is complete and valid only when:

- **Exit Status**: Process exits with code 0.
- **Artifact Verification**: If a result file was required, it exists on disk and is non-empty. A fluent stdout summary is not a substitute for the result file.
- **Schema & Format Conformance**: If `--output-format json` or `--json-schema` was specified, stdout is parseable JSON conforming to the schema.
- **Binary Identity**: `grok --version` on the executing machine matches the version expected by the invocation command.

## Available Resources & CLI Reference

### Installation & Identity Check

```bash
installer="$(mktemp)"
curl -fsSL https://x.ai/cli/install.sh -o "$installer"
# Review the script, then:
bash "$installer" 1.0.4
rm -f "$installer"
grok --version
```

- Default binary location: `$HOME/.grok/bin/grok` (with potential symlinks at `$HOME/.local/bin/grok` and `$HOME/.local/bin/agent`).
- Verification check: `grok --version` must output `grok 1.0.4` (or pinned version), and `grok models` must list xAI models (e.g., `grok-4.6`).

### Command Shapes

Single-turn from prompt file (preferred):

```bash
grok --prompt-file /absolute/path/to/prompt.md \
  --permission-mode acceptEdits \
  --output-format json \
  --cwd /absolute/path/to/scratch
```

Single-turn from argv string:

```bash
grok -p "Read /absolute/path/to/prompt.md and write the result to /absolute/path/to/result.md." \
  --permission-mode acceptEdits \
  --output-format json
```

> [!NOTE]
> `--prompt-file` is already a dedicated single-turn entry point. Do not invent non-existent subcommands like `grok print` or `grok exec`. `grok agent` is reserved for SDK transport protocols (`stdio`, `headless`, `serve`, `leader`).

### Defaults & Key Flags

| Flag | Description & Operational Boundary |
|---|---|
| `-p` / `--single` | Execute a single prompt string, print output, and exit. |
| `--prompt-file` | Execute a single prompt read from a file. |
| `--output-format` | `plain` (default), `json`, `streaming-json`, `streaming-messages-json`. |
| `--json-schema` | Constrain model output with a JSON Schema (implies `--output-format json`). |
| `--permission-mode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`. |
| `--always-approve` | Automatically approve tool executions. |
| `-m` / `--model` | Specific model ID from `grok models`. |
| `--reasoning-effort` / `--effort` | Reasoning effort for reasoning-capable models. |
| `--sandbox` | Named profile defined in `sandbox.toml` (profiles extend `workspace`). |
| `--cwd` | Explicit working directory. |
| `--tools` / `--disallowed-tools` | Built-in tool allow/deny lists. |
| `--allow` / `--deny` | Fine-grained permission rules. |
| `-c` / `--continue` | Continue the latest session in this directory. |
| `-r` / `--resume` | Resume a session by ID or title. |
| `--fork-session` | Resume into a newly created session ID. |
| `--max-turns` | Cap the maximum number of agent turns. |
| `--no-subagents` | Disable spawning child subagents. |
| `--no-plan` | Disable plan mode. |
| `--disable-web-search` | Disable built-in web search and fetch tools. |
| `-w` / `--worktree` | Interactive worktree helper (**headless `-p` does not create a worktree from this flag**). |

### Available Models (1.0.4)

Verified models listed by `grok models` on 1.0.4:
- `grok-4.20-0309-non-reasoning` (default on authoring machine)
- `grok-4.20-0309-reasoning`
- `grok-4.20-multi-agent-0309`
- `grok-4.3`, `grok-4.5`, `grok-4.6`, `grok-build-0.1`
- Built-in imagine image/video generation model IDs

Pass `-m` explicitly when a specific model variant is required.

## Enabling Guidance & Workflow Execution

### Wait Model & Execution Timing

`grok -p` and `--prompt-file` keep the process alive until the agent turn completes (identical to `claude -p` and `codex exec`). Wrappers should configure an adequate timeout and wait for clean process exit rather than polling with `sleep`.

### Headless Deep Research & Durable Report Recovery

- **Workflow Interruption Trap**: In the TUI, `/deep-research <query>` initiates a background workflow that returns immediately and posts findings later. In headless mode, passing `/deep-research …` as the prompt triggers an immediate turn termination (`stopReason: end_turn`), causing the process to exit and killing the background workflow unrecoverably.
- **Blocking Invocation Pattern**: To run deep research headlessly, instruct the model in the prompt to invoke the built-in `workflow` tool named `deep-research`, remain in the active turn until the workflow concludes, and persist the cited report to the designated result path.
- **Durable Session Recovery**: If the parent process exits 0 upon workflow completion but misses the final file write, retrieve the durable report directly from the session store:
  `~/.grok/sessions/<urlencoded-cwd>/<sessionId>/workflows/wf_*/scratch/report.md`

## Known Traps

| Trigger | Failure Mode | Remedy |
|---|---|---|
| Installing community `grok-cli` over Grok Build | Command name collision with incompatible flags | Verify identity with `grok --version` and `grok models` |
| Calling binary name `agent` | Executes wrong binary or collides with system tools | Explicitly invoke `grok` |
| Relying on `-w` in headless mode | `-p` does not create a worktree | Use `--cwd` or create the worktree prior to execution |
| Specifying undefined `--sandbox` profile name | Process refuses initialization | Define profile in `sandbox.toml` or omit `--sandbox` |
| Passing `/deep-research …` directly in headless prompt | Turn exits immediately; background workflow is terminated | Prompt model to call the `workflow` tool `deep-research` and wait |
| Unintentional `XAI_API_KEY` in environment | Forces API key billing; ignores subscription credentials | Unset `XAI_API_KEY` for the process |
| Assuming exit code 0 implies file creation | Workflow completed but parent skipped final disk write | Check result path; copy from session tree (`~/.grok/sessions/.../workflows/.../scratch/report.md`) |

## Official References

- https://x.ai/cli
- https://x.ai/cli/install.sh
