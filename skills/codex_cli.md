# Codex CLI

## Metadata

- **Type**: Tool / Focused Skill
- **Target**: Non-interactive `codex exec` invocations
- **Verified Version**: Codex CLI **0.144.6**

## Goal & Boundaries

### Goal

Execute a Codex task headlessly and recover a clean last agent message or schema-validated JSON payload directly from disk.

### When to Load

Load this file when the user asks for Codex, or when the root skill router selects `codex`.

### Boundaries & Prohibited Flags

- **Prohibited Approval Flag**: Interactive `codex` supports `-a` / `--ask-for-approval`, but **`codex exec` strictly rejects `-a`**. Verified behavior: `codex exec -a never` exits code 2 with `unexpected argument '-a' found`. Never include `-a` in exec commands.
- **Model Family**: Current Codex generation is GPT-5.x; do not copy obsolete `gpt-5.2` examples.

## Acceptance Criteria

A Codex headless run is successful only when:

- **Exit Code**: Process terminates with code 0.
- **Last Message Extraction**: The file designated by `-o` exists and contains the clean final agent message (not raw event logs).
- **Schema Conformance**: If `--output-schema` was specified, the `-o` output file validates against that JSON Schema.
- **Task Artifacts**: If a dedicated result file was required in the prompt, that file exists on disk and is non-empty.

## Available Resources & CLI Reference

### Command Shape

```bash
codex exec --skip-git-repo-check --sandbox read-only --color never \
  -c model_reasoning_effort=low \
  --output-schema /absolute/path/to/schema.json \
  -o /absolute/path/to/last_message.json \
  "Read /absolute/path/to/prompt.md and follow it exactly."
```

- Subcommand alias: `exec` may be abbreviated as `e`.
- Stdin input: A prompt argument of `-` reads from stdin. If both a positional prompt and stdin are provided, stdin is appended inside a `<stdin>` block.

### Defaults & Key Flags

| Flag | Description & Operational Boundary |
|---|---|
| `-m` / `--model` | Target model id (GPT-5.x generation). |
| `-c model_reasoning_effort=` | Reasoning effort override: `low`, `medium`, `high`. (Configuration override, not a standalone flag). |
| `-s` / `--sandbox` | Sandbox boundary: `read-only` (for reasoning-only tasks), `workspace-write` (for file edits), or `danger-full-access`. |
| `--dangerously-bypass-approvals-and-sandbox` | Bypass sandbox; use only when an outer isolation sandbox is already active. |
| `--skip-git-repo-check` | Required when running outside a git repository (e.g., in `/tmp`). |
| `--ephemeral` | Do not persist session files on disk. |
| `-C` / `--cd` | Set agent working directory root. |
| `--add-dir` | Add extra writable directory. |
| `--color never` | Suppress ANSI escape codes in stdout. |
| `-o` / `--output-last-message` | Path to write the clean final agent message. Prefer this over stdout parsing. |
| `--output-schema` | JSON Schema file path to constrain and validate the `-o` final message. |
| `--json` | Stream JSONL event lines on stdout. |
| `-i` / `--image` | Attach image files to the prompt. |
| `--ignore-user-config` | Skip `$CODEX_HOME/config.toml` (authentication still resolves via `CODEX_HOME`). |

### Additional Automation Commands

- `codex exec resume <session_id>` or `--last`
- `codex review` / `codex exec review`
- `codex sandbox <command...>`
- `codex doctor`

## Enabling Guidance & Features

### JSONL Event Stream

When `--json` is enabled, stdout emits event objects (`thread.started`, `turn.started`, `item.completed`, `turn.completed`). The final answer is inside an `item` object where `type == "agent_message"` with a `text` field. Occasional stderr notices regarding cache TTL can be safely ignored.

### Built-in Image Generation

Codex can trigger its built-in `imagegen` capability directly from a natural-language exec prompt. Instruct it to generate images and pass reference attachments using `--image` if necessary. Output images are typically saved in the session's `generated_images/` directory within the Codex home directory. Stdout may not output the exact path; inspect the `generated_images/` directory upon process completion. This uses the Codex / ChatGPT subscription rather than a separate image API.

## Known Traps

| Trigger | Failure Mode | Remedy |
|---|---|---|
| Passing `-a never` to `codex exec` | Immediate CLI parse error (`unexpected argument '-a' found`) | Omit `-a`; configure isolation via `--sandbox` |
| Scraping unformatted stdout | Output polluted with event objects, warnings, and ANSI codes | Use `-o` for message file and specify `--color never` |
| Executing in `/tmp` without `--skip-git-repo-check` | Exec refuses to run outside a git repository | Pass `--skip-git-repo-check` or use `--cd` to point to a repository |
| Omitting `--ephemeral` on one-shot runs | Session rollout files accumulate indefinitely on disk | Supply `--ephemeral` for one-off automation runs |

## Official References

- https://developers.openai.com/codex
