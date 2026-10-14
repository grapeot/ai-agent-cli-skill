# AI Agent CLI Skill

A filesystem-native skill pack for calling coding-agent CLIs from another agent or script, including live Claude Code session control. It covers Claude Code, Codex, OpenCode, Antigravity, Grok Build, and Cursor.

The product is Markdown, not a new wrapper binary. File-producing one-shot work is verified against its result artifact; live session work is verified against the exact running object, correlated messages and results, and requested artifacts without requiring the worker to exit.

## What this gives you

- One root skill that decides *whether* to call a CLI agent and *which* one
- One focused skill per CLI with verified flags, defaults, and failure modes
- A shared file-response pattern so pipelines do not depend on pipe-friendly models
- Claude local discovery and inbox messaging, SDK-hosted Remote Control, internal controller boundaries, and a verified normal-tools auto working configuration

This skill pack is designed for autonomous agents and scripts. Humans can read it, but the acceptance criteria are written for programmatic verification.

## Install

Hand this repository to your coding agent:

```text
Install this public skill repo into my workspace:
https://github.com/grapeot/ai-agent-cli-skill

Start from my workspace AGENTS.md or CLAUDE.md. Follow any WORKSPACE.md or skills/INDEX.md routing rules. Clone or vendor the repo under an appropriate project directory. Expose exactly one root skill to my global skill index or agent instructions. Keep private aliases, local paths, credentials, endpoint defaults, and business context in a local overlay, not in the public repo.
```

The installer should:

1. Clone or vendor the repo.
2. Point the workspace discovery chain at `skills/skill_ai_agent_cli.md` only.
3. Leave all vendor-focused files and supporting references inside this repo, loaded on demand; do not create a separate symlink or private overlay for an individual sub-skill.
4. Use a single root symlink when no private policy is needed; otherwise use one root overlay pointing to the canonical root. Resolve relative routes from the canonical root's real directory, not the alias directory. Keep machine paths, credentials, and task state out of this public repo.

Each CLI must still be installed and logged in on the machine running it.

## When to load which file

| File | Load when |
|---|---|
| `skills/skill_ai_agent_cli.md` | Choosing a CLI, writing an automation pipeline, or routing execution |
| `skills/claude_code.md` | Running Claude Code one-shot tasks, normal tools with auto mode, existing-session control, or Remote Control |
| `skills/references/claude_sessions.md` | Loaded on demand by `claude_code.md` for live session and Remote Control details; not an additional global entry |
| `skills/codex_cli.md` | Running `codex exec` |
| `skills/opencode_cli.md` | Running `opencode run` or `opencode serve` |
| `skills/antigravity_cli.md` | Running `agy --print` |
| `skills/grok_cli.md` | Running `grok -p` or `grok --prompt-file` |
| `skills/cursor_cli.md` | Running `cursor agent -p` |

## Verified versions

Vendor baselines are listed below. Claude help and live-session capabilities were re-verified on 2026-10-14; other rows retain their own documented verification scope rather than inheriting that date.

| CLI | Command | Version |
|---|---|---|
| Claude Code | `claude`; Agent SDK | CLI 2.1.299 / SDK 0.3.299: live control, Remote, normal workspace tools and auto; earlier one-shot baseline 2.1.220 |
| Codex CLI | `codex` | 0.156.1 |
| Antigravity | `agy` | 1.1.13 |
| Grok Build | `grok` | 1.0.4 |
| OpenCode | `opencode` | official CLI docs dated 2026-08-16 |
| Cursor | `cursor agent` | launcher 3.16.17 / agent CLI 2026.08.11-e8db854 |

Re-run `--help` before trusting an older copy of a focused skill.

## Privacy

This repository is meant to be public. Examples use `example.com` paths and fake keys. Keep subscription tokens, workspace roots, and private wrapper rules out of this repo.

## License

MIT
