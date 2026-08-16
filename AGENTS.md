# AGENTS.md — AI Agent CLI Skill

## Project identity

Public, English, filesystem-native skill pack for calling coding-agent CLIs from another agent or script. The product is the Markdown in `skills/`. There is no runtime package.

## Layout

```text
ai_agent_cli_skill/
├── AGENTS.md
├── README.md
├── skills/
│   ├── skill_ai_agent_cli.md   # root / router — expose only this globally
│   ├── claude_code.md
│   ├── codex_cli.md
│   ├── opencode_cli.md
│   ├── antigravity_cli.md
│   └── grok_cli.md
├── docs/
├── tests/
└── .github/workflows/ci.yml
```

## Constraints

1. This is a public repo. Use fake examples only. No real emails, phones, API keys, password-manager vault paths, internal hostnames, or machine-specific home paths.
2. Expose exactly one root skill to a workspace index. Focused files are loaded on demand.
3. English only in docs, skills, tests, and commit messages.
4. After a substantive change, append a dated bullet under `docs/working.md` → Changelog, and record real pitfalls under Lessons Learned.
5. Commit only when the user asks. Prefer small, reversible commits.
6. Re-verify CLI help before changing a flag. Do not keep flags that the current binary rejects.

## Verification

```bash
python3 tests/test_public_hygiene.py
```

CLI interface claims must be checked against the local binaries (or current official docs for OpenCode when the binary is absent). Record the verified version in the focused skill.

## Git

Default branch: `master`.
