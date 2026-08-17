# Working log

## Changelog

### 2026-08-16

- Rewrote all six skill files to the meta-skill shape (goal, acceptance, resources, enabling guidance, real traps) without changing CLI facts. Restored two AGY drift items: Codex resume stays `codex exec resume <session_id>` or `--last` (not `codex exec --last`); Antigravity stderr check stays “no unhandled error,” not “fatal errors only.”
- Documented Grok headless wait model: `-p` blocks until the turn ends, but a prompt that is only `/deep-research` returns immediately, kills the background workflow on exit, and cannot resume. Use the built-in `workflow` tool in-turn. `XAI_API_KEY` overrides stored subscription login. Exit 0 is not enough if the parent skipped the result file; recover from `~/.grok/sessions/.../workflows/.../scratch/report.md`.
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
- Grok `/deep-research` is a background workflow, not a long foreground turn. Headless `-p` with that slash command as the whole prompt exits in seconds; session shutdown then marks the run interrupted and unrestorable. Invoking the same built-in via the `workflow` tool keeps the parent turn open until Plan → Research → Verify → Report finish.
- On 1.0.4, a set `XAI_API_KEY` wins over `~/.grok/auth.json`. `grok models` is the check. Remote login is `--device-auth`, not `--oauth`.
- A completed Grok workflow can still leave the caller-requested result file unwritten. The durable report lives under the session workflow scratch directory.
- A form-only rewrite still needs a fact audit. AGY expanded `codex exec resume … or --last` into `codex exec --last`, and narrowed Antigravity’s stderr check to “fatal” errors. Both looked like cleanup. Compare command tokens, not just section titles.
