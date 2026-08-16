# Working log

## Changelog

### 2026-08-16

- Scaffolded the public skill pack: docs, root router, five focused CLI skills, hygiene tests, CI.
- Verified local binaries: Claude Code 2.1.220, Codex 0.144.6, Antigravity 1.1.13, Grok Build 1.0.4.
- Confirmed official Grok stable channel reports 1.0.4; installed that version to `~/.grok/bin/grok`.
- Documented OpenCode from official CLI docs dated 2026-08-16 because `opencode` was not on PATH in the authoring shell.
- Recorded Codex `exec` rejecting `-a/--ask-for-approval`.
- Recorded Antigravity 1.1.13 adding `--output-format json|stream-json` and `--json-schema`; default `--print-timeout` is 5m.
- Privacy review on `privacy-review`: `python3 tests/test_public_hygiene.py` passed. Manual `rg` for home paths, vault refs, internal hosts, and token prefixes only hit the scanner's own patterns plus the documented Codex `-a` rejection. No live credentials or machine paths in tracked files.

## Lessons Learned

- `codex exec` and interactive `codex` no longer share the same approval flag. Testing `codex exec -a never --help` is the check; reading top-level `codex --help` is not enough.
- Antigravity help can gain JSON flags without adding an `agy run` subcommand. Keep treating `--print` as the headless entry.
- xAI's installer also links `~/.local/bin/agent` to Grok. That name collides with other tools; automation should call `grok`, not `agent`.
- The community project `superagent-ai/grok-cli` also installs a `grok` binary under `~/.grok/bin`. Version output plus `grok models` is the identity check.
