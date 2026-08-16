# Grok Build CLI

Non-interactive `grok` invocations. Verified against Grok Build **1.0.4** (`grok 1.0.4 (d846eb93d94d)`). Official stable channel reported 1.0.4 on 2026-08-16.

This is xAI's Grok Build CLI. It is not Groq, and it is not the community `superagent-ai/grok-cli` binary that also names itself `grok`.

## Goal

Run a Grok coding-agent turn from a prompt file, recover stdout or JSON, and optionally have the agent write a result file.

## When to load this file

The user asked for Grok / Grok Build / `grok` CLI, or the root skill selected it.

## Install

Review, then run, the official installer. Pin the version when you care about flag stability:

```bash
installer="$(mktemp)"
curl -fsSL https://x.ai/cli/install.sh -o "$installer"
# Review the script, then:
bash "$installer" 1.0.4
rm -f "$installer"
grok --version
```

Default binary path is `$HOME/.grok/bin/grok`. The installer may also link `$HOME/.local/bin/grok` and `$HOME/.local/bin/agent`. Call `grok`, never `agent` — `agent` is a generic name.

Identity check after install:

- `grok --version` starts with `grok 1.0.4` (or the pinned version)
- `grok models` lists xAI model ids such as `grok-4.6`

If version output or model names look like another project, you have the wrong binary on PATH.

Auth is `grok login` (subscription / OAuth) or `XAI_API_KEY`. `grok models` reports which path is active.

## Command shape

Single-turn from argv:

```bash
grok -p "Read /absolute/path/to/prompt.md and write the result to /absolute/path/to/result.md." \
  --permission-mode acceptEdits \
  --output-format json
```

Single-turn from a file (preferred):

```bash
grok --prompt-file /absolute/path/to/prompt.md \
  --permission-mode acceptEdits \
  --output-format json \
  --cwd /absolute/path/to/scratch
```

`--prompt-file` is already a single-turn path. Do not invent `grok print` or `grok exec`.

`grok agent` starts SDK transports (`stdio`, `headless`, `serve`, `leader`). Use it only when you are wiring those protocols. Default automation is `-p` / `--prompt-file`.

## Defaults that matter

| Flag | Use |
|---|---|
| `-p` / `--single` | One prompt, print, exit |
| `--prompt-file` | One prompt from a file |
| `--output-format` | `plain` (default), `json`, `streaming-json`, `streaming-messages-json` |
| `--json-schema` | Constrains the model; implies `--output-format json` |
| `--permission-mode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` |
| `--always-approve` | Auto-approve tool executions |
| `-m` / `--model` | Model id from `grok models` |
| `--reasoning-effort` / `--effort` | Reasoning models |
| `--sandbox` | Named profile from `sandbox.toml` (profiles extend `workspace`) |
| `--cwd` | Working directory |
| `--tools` / `--disallowed-tools` | Built-in tool allow/deny lists |
| `--allow` / `--deny` | Permission rules |
| `-c` / `--continue` | Continue the latest session in this directory |
| `-r` / `--resume` | Resume by id or title |
| `--fork-session` | Resume into a new session id |
| `--max-turns` | Cap agent turns |
| `--no-subagents` | Disable child agents |
| `--no-plan` | Disable plan mode |
| `--disable-web-search` | Drop web search/fetch tools |
| `-w` / `--worktree` | Interactive worktree helper; **headless `-p` does not create a worktree from this flag** |

`grok models` on 1.0.4 listed at least: `grok-4.20-0309-non-reasoning` (default on the authoring machine), `grok-4.20-0309-reasoning`, `grok-4.20-multi-agent-0309`, `grok-4.3`, `grok-4.5`, `grok-4.6`, `grok-build-0.1`, plus imagine image/video ids. Pass `-m` when you care which one runs.

## Completion check

- Exit code 0
- If a result file was required: it exists and is non-empty
- If `--output-format json` or `--json-schema` was set: stdout is parseable JSON and matches the schema
- `grok --version` on that machine matches the skill you wrote the command from

## Known traps

| Trap | What happens | What to do |
|---|---|---|
| Installing community `grok-cli` over Grok Build | Same command name, different flags | Check `--version` and `grok models` |
| Calling `agent` | Wrong binary or a name collision | Call `grok` |
| Assuming `-p` creates a worktree | Docs say it does not | Use `--cwd` or an interactive worktree |
| Custom `--sandbox` name with no profile | Process refuses to start | Define the profile or omit the flag |

## Official docs

- https://x.ai/cli
- https://x.ai/cli/install.sh
