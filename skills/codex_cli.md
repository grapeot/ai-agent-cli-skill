# Codex CLI

Non-interactive `codex exec` invocations. Verified against Codex CLI **0.144.6**.

## Goal

Run a Codex task headlessly and recover a clean last message or schema-valid JSON from disk.

## When to load this file

The user asked for Codex, or the root skill selected `codex`.

## Command shape

```bash
codex exec --skip-git-repo-check --sandbox read-only --color never \
  -c model_reasoning_effort=low \
  --output-schema /absolute/path/to/schema.json \
  -o /absolute/path/to/last_message.json \
  "Read /absolute/path/to/prompt.md and follow it exactly."
```

`exec` may be spelled `e`. A prompt of `-` reads stdin. If both a positional prompt and stdin are present, stdin is appended as a `<stdin>` block.

## Defaults that matter

| Flag | Use |
|---|---|
| `-m` / `--model` | Model id. Current Codex generation is GPT-5.x; do not copy old `gpt-5.2` examples. |
| `-c model_reasoning_effort=` | `low` / `medium` / `high`. This is a config override, not a standalone flag. |
| `-s` / `--sandbox` | `read-only`, `workspace-write`, `danger-full-access` |
| `--dangerously-bypass-approvals-and-sandbox` | Only when an outer sandbox already exists |
| `--skip-git-repo-check` | Required outside a git repo |
| `--ephemeral` | Do not persist session files |
| `-C` / `--cd` | Agent working root |
| `--add-dir` | Extra writable directory |
| `--color never` | Strip ANSI from stdout |
| `-o` / `--output-last-message` | Clean last agent message on disk. Prefer this over scraping stdout. |
| `--output-schema` | JSON Schema file for the final message. Works with `-o`. |
| `--json` | JSONL event stream on stdout |
| `-i` / `--image` | Attach image files |
| `--ignore-user-config` | Skip `$CODEX_HOME/config.toml`; auth still uses `CODEX_HOME` |

Interactive `codex` still has `-a` / `--ask-for-approval`. **`codex exec` rejects `-a`.** Verified: `codex exec -a never` exits 2 with `unexpected argument '-a' found`. Do not copy that flag into exec commands.

For file writes use `--sandbox workspace-write`. For reasoning-only use `read-only`.

## JSONL events

`--json` emits events such as `thread.started`, `turn.started`, `item.completed`, `turn.completed`. The final answer is an `item` with `type == "agent_message"` and a `text` field. Ignore occasional stderr lines about cache TTL.

## Other automation commands

- `codex exec resume <session_id>` or `--last`
- `codex review` / `codex exec review`
- `codex sandbox <command...>`
- `codex doctor`

## Image generation

Codex can trigger built-in `imagegen` from a natural-language exec prompt. Ask it to use imagegen and attach references with `--image` when needed. Generated files usually land under the Codex home `generated_images/` directory for that session. Stdout may not print the path; inspect that directory after the run. This uses the Codex / ChatGPT subscription, not a separate image-API skill.

## Completion check

- Exit code 0
- `-o` file exists and is the last message, not an event dump
- If `--output-schema` was set: the `-o` file validates
- If a result file was required in the prompt: that file exists and is non-empty

## Known traps

| Trap | What happens | What to do |
|---|---|---|
| `codex exec -a never` | Immediate clap error | Drop `-a`; use `--sandbox` |
| Parsing mixed stdout | Events, warnings, ANSI | `-o` plus `--color never` |
| Running in `/tmp` without `--skip-git-repo-check` | Exec refuses | Pass the flag or `--cd` into a repo |
| Leaving sessions on disk | Rollout files pile up | `--ephemeral` for one-shots |

## Official docs

- https://developers.openai.com/codex
