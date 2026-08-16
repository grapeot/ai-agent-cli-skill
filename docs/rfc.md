# RFC: AI Agent CLI Skill

## Decision

Ship a public skill pack with exactly one workspace-facing root file. Put each vendor CLI in its own focused file. Keep private paths and wrapper policy in the consuming workspace.

## Why split

One file is easier to open and worse to maintain. Claude and Antigravity already needed their own contracts. Codex, OpenCode, and Grok are now the same size. A router plus focused files matches how this workspace installs every other multi-skill public repo.

The root file answers: should I call a CLI agent, which one, and what is the shared I/O contract?

A focused file answers: what is the current command shape, what must be true before I start, and how do I know it finished?

## File-response contract

Production calls use three artifacts:

1. A task file the child agent must read
2. A result file the child agent must write
3. Captured stdout, stderr, and any vendor log file

Stdout is a completion note, not the product. If the result file is missing or empty, the call failed even when the process exited 0.

Do not pipe the task body through stdin unless the vendor CLI documents stdin as the prompt channel *and* the prompt is short enough to audit. Prefer `--prompt-file` / "read this path" driver prompts.

## Public / private split

Public files may mention:

- Vendor install URLs
- Flag names and verified versions
- Generic paths such as `/tmp/example-session/` or `$PWD/tmp/`

Public files must not mention:

- A specific home directory or company monorepo
- Real emails, phones, or vault paths
- One workspace's subagent-wrapping policy, except as a generic warning against unbounded nesting

A consuming workspace should add a private overlay when it needs a fixed start directory, a required model, or a local wrapping rule.

## CLI-specific notes

### Claude Code

Headless entry is `claude -p`. `--tools` still exists. `--effort` is valid again on 2.1.220. Do not treat a Claude-routed subagent as Claude Code.

### Codex

Headless entry is `codex exec`. On 0.144.6, `codex exec` rejects `-a/--ask-for-approval`. Use `--sandbox` and `-o` / `--output-schema`.

### OpenCode

`opencode run` is valid on its own. `serve` plus `--attach` is an optimization for cold start and session control, not a required two-step.

### Antigravity

Headless entry is top-level `agy --print`. There is no `agy run`. 1.1.13 adds `--output-format json|stream-json` and `--json-schema`. Default `--print-timeout` is 5m.

### Grok Build

This is xAI's `grok` CLI, not the community `superagent-ai/grok-cli` and not Groq. Headless entry is `grok -p` or `grok --prompt-file`. `grok agent` is the SDK/stdio transport, not the default automation path.

## Testing

There is no live-CLI CI. Tests check repo shape and public hygiene. Interface drift is caught by re-reading `--help` when a skill is edited.

## Alternatives rejected

- One giant guide: already failed to stay current.
- A Python wrapper around all five CLIs: another compatibility surface, no user request.
- Vendor skill folders such as `.claude/skills`: this pack is tool-agnostic Markdown.
