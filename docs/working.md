# Working log

## Changelog

### 2026-09-23

- Re-verified Codex against the live binary **0.156.1**: `codex exec` now rejects `--full-auto` and `--ask-for-approval` in addition to `-a` (all `unexpected argument`, exit 2); `-o/--output-last-message`, `--json`, `--ephemeral`, and `-c` overrides are unchanged.
- Documented two 0.156.1 pitfalls in `skills/codex_cli.md`: (1) multiple global npm install roots make `codex update` silently miss the binary actually on `PATH`, producing an endless "upgrade available" loop — repaired by upgrading the stale root with `npm install -g @openai/codex --prefix <root>`; (2) the CLI declares a `web_search` tool by default, which 400s on OpenAI-compatible backends without it — disabled via bare top-level `web_search = "disabled"` in the profile config (the key is a string unit variant; `false` is rejected on 0.156.1).
- Replaced the removed approval flags in the documented command shape with `--sandbox` + `-c approval_policy="never"`.

### 2026-09-21

- Re-verified Antigravity against the live binary: CLI is now **1.2.0**. `agy models` list is unchanged (gemini-3.8/3.7/3.6 flash, gemini-3.1-pro, claude-sonnet-4-6, claude-opus-4-6-thinking, gpt-oss-120b-medium). `--help` confirms no `login` / `run` subcommands; `--print-timeout` default changed from 5m to `0` (wait until the turn completes); new flags `--agent`, `--disable-slash-commands`, `-i/--prompt-interactive`, `--input-format` (NDJSON stdin), `--remote-control`, `--prompt` alias, and the `mic-serve` subcommand.
- Ran a live one-shot `agy --print` with `--new-project --output-format json` on `gemini-3.8-flash-high`: exit 0, clean stderr, artifact materialized in the intended scratch directory. `--output-format json` stdout on 1.2.0 is a single object with `conversation_id`, `status: "SUCCESS"`, `response`, `duration_seconds`, `num_turns`, and `usage`; documented the shape and kept result-file verification as the acceptance gate.
- Updated `skills/antigravity_cli.md`: verified version 1.2.0, `--print-timeout` default change, JSON schema note, 1.2.0 flag additions, and trap-table wording.

### 2026-09-10

- Re-verified Cursor launcher 3.19.7 and agent 2026.09.08-6caf4ff, including help, model availability and a successful Gemini 3.8 Flash High JSON turn. Kept the explicit model default and added root routing, file-result read-back, separate log capture, independent-session flags and parent-owned timeout guidance.
- Removed the unsupported implication that API-key authentication alone establishes separate billing. Kept task-specific writing policy in callers and left all Antigravity documentation unchanged.

### 2026-09-05

- Re-verified Antigravity against the live binary: CLI is now **1.1.27**. `agy models` list is unchanged from 1.1.26; `--help` confirms no `login` / `run` subcommands, `--print-timeout` default still 5m0s, and new `--new-project` / `--project` flags.
- Documented a session-scoping trap found in live use: a bare `agy --print` (no resume flags) does not start a clean session — the run resumes the project's most recent conversation, and project scope walks up from cwd, so a fresh scratch directory under the same workspace inherits the previous task's context. Observed failure: AGY re-executed the old task and wrote the artifact into the old scratch tree, exit code 0. Added `--new-project` / `--project` to the flag table, removed the incorrect "fresh session" claim on `--conversation`, added the trap to Known Traps, and tightened the artifact-materialization acceptance criterion to require the intended path.

### 2026-09-04

- Re-verified Antigravity against the live binary: CLI is now **1.1.26**. `agy models` lists `gemini-3.8-flash-high/medium/low` (3.5 Flash IDs no longer listed); `--print-timeout` default is still 5m; still no `login` subcommand. Changed the skill default model from `gemini-3.7-flash-high` to `gemini-3.8-flash-high` (command shape, `--model` row, available-models list) and bumped the verified version.
- Re-verified Cursor: launcher is now **3.17.19** (agent CLI still **2026.08.11-e8db854**). `--list-models` confirms `gemini-3.8-flash-high/medium/low` available. Updated `skills/cursor_cli.md` default model to `gemini-3.8-flash-high`, added 3.8 to the models list, and bumped the verified version.

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
- A bare `agy --print` is not session-isolated. Project scope walks up from cwd, so any scratch directory under the same workspace resumes the project's most recent conversation — the agent happily re-executes the old task and writes the artifact into the old directory, with exit code 0. One-shot tasks need `--new-project` (or an explicit `--project`), and acceptance must verify the artifact path, not just its existence.
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

- Codex removed `--full-auto` between 0.14x and 0.15x. Automation that hardcoded it fails with `unexpected argument` on the first turn of every run; the approval knob is now a config override, `-c approval_policy="never"`.
- `codex update` upgrades the npm prefix that owns `npm`, not the binary that owns `PATH`. With two global roots, the stale one wins on `PATH` and the upgrade prompt loops forever even though each update reports success. `which -a codex` plus comparing each root's `package.json` version is the diagnostic; `npm install -g @openai/codex --prefix <stale-root>` is the repair.
- A newer Codex CLI can break non-OpenAI providers with no local error: the default `web_search` tool declaration is rejected (HTTP 400) by the provider. The fix is bare top-level `web_search = "disabled"` in the config the run actually loads (profile files layer over the base config). The key is a string unit variant — `codex doctor -c web_search=<value>` is the cheap way to probe which strings parse without an API call.
- `codex exec` and interactive `codex` no longer share the same approval flag. Testing `codex exec -a never --help` is the check; reading top-level `codex --help` is not enough.
- Antigravity help can gain JSON flags without adding an `agy run` subcommand. Keep treating `--print` as the headless entry.
- xAI's installer also links `~/.local/bin/agent` to Grok. That name collides with other tools; automation should call `grok`, not `agent`.
- The community project `superagent-ai/grok-cli` also installs a `grok` binary under `~/.grok/bin`. Version output plus `grok models` is the identity check.
- Grok `/deep-research` is a background workflow, not a long foreground turn. Headless `-p` with that slash command as the whole prompt exits in seconds; session shutdown then marks the run interrupted and unrestorable. Invoking the same built-in via the `workflow` tool keeps the parent turn open until Plan → Research → Verify → Report finish.
- On 1.0.4, a set `XAI_API_KEY` wins over `~/.grok/auth.json`. `grok models` is the check. Remote login is `--device-auth`, not `--oauth`.
- A completed Grok workflow can still leave the caller-requested result file unwritten. The durable report lives under the session workflow scratch directory.
- A form-only rewrite still needs a fact audit. AGY expanded `codex exec resume … or --last` into `codex exec --last`, and narrowed Antigravity’s stderr check to “fatal” errors. Both looked like cleanup. Compare command tokens, not just section titles.
