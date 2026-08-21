# Working log

## Changelog

### 2026-08-20

- Re-verified Cursor against the live binaries: launcher still **3.16.17**, agent CLI is now **2026.08.11-e8db854**. Updated `skills/cursor_cli.md`.
- Documented headless resume: `create-chat` returns a UUID; `--resume <id> -p` plus a new prompt is the next turn. There is no `append` subcommand. `ls` / bare `resume` are interactive TUI, not a scriptable listing.
- Documented `--model` bracket overrides (`'claude-opus-4-8[context=1m,effort=high,fast=false]'`) alongside the existing `-fast` suffix IDs. Gemini 3.7 Flash still has no `-fast` variant.
- Added headless-relevant flags that help now lists: `--approve-mcps`, `--auto-review`, `--add-dir`, `--skip-worktree-setup`. Noted `plugin` / `worker` / `bedrock` as out of scope for a normal `-p` turn.
- Dropped stale `composer-1` as CLI default. `--list-models` lists `auto` as default; `cursor agent about` on this machine showed Gemini 3.7 Flash High as the current model.
- Aligned the JSON success shape with current docs (`session_id`, `duration_ms`); do not require a `usage` block.

### 2026-08-18

- Added `skills/cursor_cli.md` and routed it from the root skill. Verified against local binaries: Cursor IDE launcher 3.16.17 ships agent CLI 2026.05.01; headless entry is `cursor agent -p` with `--output-format text|json|stream-json`, `--mode plan|ask`, `--trust`, `--sandbox`, `--workspace`, `-w` worktree, and `--resume/--continue`.
- Verified `gemini-3.7-flash-high` end-to-end on Cursor (file-task creation, text reply, JSON result envelope with usage). `gemini-3.7-flash-low` also works.
- Recorded the "fast" finding: fast is a model-ID `-fast` suffix, not a flag; Gemini 3.7 Flash has no `-fast` variant; and on 2026-08-18 all `-fast` routes tested (`composer-2.5-fast`, `cursor-grok-4.6-medium-fast`) failed with relay connection retries while base models worked.
- Recorded the login trap: CLI tokens live in macOS Keychain (`cursor-access-token`/`cursor-refresh-token`) and are separate from IDE login; the browser challenge needs the waiting `cursor agent login` process alive to receive the callback.
- Privacy review on the Cursor addition: `python3 tests/test_public_hygiene.py` passed; manual scan found no real emails, home paths, or credentials in tracked files.

## Lessons Learned
- Cursor's auth split bites quietly: the IDE can be logged in (SQLite state) while the CLI holds months-old Keychain tokens. `cursor agent about` is the check; a fresh `cursor agent login` rewrites both entries.
- Cursor model errors and auth errors can exit 0 when piped. Wrappers must inspect stdout for the error line or the JSON `is_error` field, not just the exit code.
- "Fast" on Cursor is still not a `--fast` flag. Prefer a `-fast` suffix ID from `--list-models`, or a quoted `[fast=false]` / `[fast=true]` bracket override on `--model`. Those `-fast` routes can be down independently of base models.
- Headless follow-ups are `--resume <session_id> -p "next prompt"`, not `ls`. `create-chat` is the scriptable way to mint an ID; JSON `session_id` is the durable handle. Do not treat IDE Composer threads as CLI chats.

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
