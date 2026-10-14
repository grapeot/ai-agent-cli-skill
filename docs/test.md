# Test Strategy

## Definition of Done

A documentation or skill change is complete when all of the following criteria are met:

1. **Required Files**: All declared repository and skill documents exist in their expected locations.
2. **Single-Entry Exposure**: Only `skills/skill_ai_agent_cli.md` is exposed to workspace skill indexes.
3. **Hygiene Verification**: No private emails, personal home paths, password-manager vault URIs, PEM keys, or active credentials appear in tracked files.
4. **Verified Baseline**: Every focused skill explicitly records a verified version marker and an unambiguous completion gate.
5. **Clean Offline Verification**: Offline validation tests pass without warnings or errors.
6. **Canonical Link Resolution**: Relative links to focused skills and internal references resolve properly from the canonical root file, without requiring per-sub-skill symlinks or overlays.

## Offline Contract & Hygiene Tests

The repository includes a dependency-free test script at `tests/test_public_hygiene.py`.

It validates:
- Presence of all required markdown documents, skills, and configuration files.
- Inclusion of all focused skills within the root router (`skills/skill_ai_agent_cli.md`).
- Presence of verified-version markers across all vendor-focused skills.
- Absence of real machine home directory paths (such as macOS home paths).
- Absence of private hostnames, disallowed email addresses, password-manager references, private key headers, and credential assignments.

Run the test suite:

```bash
python3 tests/test_public_hygiene.py
```

## Live CLI Verification & Integration Testing

Live integration tests are excluded from continuous integration pipelines because vendor tools require authenticated subscriptions, spend interactive quota, and depend on local machine state.

### Author Verification Workflow

When updating a focused skill:
1. Re-verify the binary flags against the live tool using `--help` and `--version` (or consult official online documentation when the binary is unavailable).
2. Update the documented `Verified Version` metadata to reflect the re-verified version and date.
3. When separately authorized and needed, a useful smoke test writes a known verification marker (such as `CLI_SMOKE_OK`) to a temporary result file. Do not commit it. A documentation-only edit does not itself authorize new sessions, restarts, or quota-spending calls.

### Live Claude Session Verification Scope

Live experiments conducted on 2026-10-14 utilized an explicitly authorized, peer-accepting Claude Code instance (CLI 2.1.299, SDK 0.3.299) to verify:
- Correlation of local session UUIDs, live PIDs, and config registry records.
- Line-delimited JSON frame delivery via Unix domain sockets.
- Session continuity under SDK-hosted Remote Control.
- Direct HTTP controller interactions (event listing, SSE streaming, message dispatch, and interrupt control).
- Bidirectional UUID matching for iOS-initiated turns.
- Normal workspace tool execution (Bash `pwd`/date, Write probes, Read verification) under effective auto mode with zero manual permission approvals.

These live tests are performed manually on dedicated targets and are never run automatically in CI.

## Rationale for Omitting CI End-to-End Suites

Default public CI is deliberately unauthenticated and receives no vendor session credentials or subscription quota. Live vendor agents also depend on local state. Mocking a subprocess would test the mock rather than actual vendor behavior.

## Manual Pre-Publish Audit

Before publishing changes or after significant revisions, execute a manual pattern scan:

```bash
rg -n "@|/Users/|BEGIN (RSA |OPENSSH )?PRIVATE KEY" --glob '!.git/**'
```

Examine all search matches carefully to confirm that no private information or real machine paths have been introduced.
