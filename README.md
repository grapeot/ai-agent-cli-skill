# AI Agent CLI Skill

A filesystem-native skill pack for calling coding-agent CLIs from another agent or script. It covers Claude Code, Codex, OpenCode, Antigravity, and Grok Build.

The point is not a new wrapper binary. The point is a stable contract: write the task to a file, run the vendor CLI non-interactively, and treat the result file as the only success signal.

## What this gives you

- One root skill that decides *whether* to call a CLI agent and *which* one
- One focused skill per CLI with verified flags, defaults, and failure modes
- A shared file-response pattern so pipelines do not depend on pipe-friendly models

This is for agents and automation. Humans can read it, but the acceptance criteria are written for another program.

## Install

Hand this repository to your coding agent:

```text
Install this public skill repo into my workspace:
https://github.com/grapeot/ai-agent-cli-skill

Start from my workspace AGENTS.md or CLAUDE.md. Follow any WORKSPACE.md or skills/INDEX.md routing rules. Clone or vendor the repo under an appropriate project directory. Expose exactly one root skill to my global skill index or agent instructions. Keep private aliases, local paths, credentials, endpoint defaults, and business context in a local overlay, not in the public repo.
```

The installer should:

1. Clone or vendor the repo
2. Point the workspace discovery chain at `skills/skill_ai_agent_cli.md` only
3. Leave `claude_code.md`, `codex_cli.md`, `opencode_cli.md`, `antigravity_cli.md`, and `grok_cli.md` as on-demand files inside this repo
4. Put private workspace paths and wrapper rules in a local overlay

Each CLI still has to be installed and logged in on the machine that will run it.

## When to load which file

| File | Load when |
|---|---|
| `skills/skill_ai_agent_cli.md` | Choosing a CLI, writing a pipeline, or invoking any of these tools |
| `skills/claude_code.md` | Running `claude -p` |
| `skills/codex_cli.md` | Running `codex exec` |
| `skills/opencode_cli.md` | Running `opencode run` / `opencode serve` |
| `skills/antigravity_cli.md` | Running `agy --print` |
| `skills/grok_cli.md` | Running `grok -p` / `grok --prompt-file` |

## Verified versions

Recorded on 2026-08-16:

| CLI | Command | Version |
|---|---|---|
| Claude Code | `claude` | 2.1.220 |
| Codex CLI | `codex` | 0.144.6 |
| Antigravity | `agy` | 1.1.13 |
| Grok Build | `grok` | 1.0.4 |
| OpenCode | `opencode` | official CLI docs dated 2026-08-16 |

Re-run `--help` before trusting an older copy of a focused skill.

## Privacy

This repository is meant to be public. Examples use `example.com` paths and fake keys. Keep subscription tokens, workspace roots, and private wrapper rules out of this repo.

## License

MIT
