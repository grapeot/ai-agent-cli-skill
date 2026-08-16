# Test strategy

## What "done" means

1. Required files exist.
2. The root skill is the only file a workspace index should expose.
3. Public files contain no private-data patterns.
4. Each focused skill names a verified version and a completion check.
5. Offline hygiene tests pass in CI.

## Unit / contract tests

`tests/test_public_hygiene.py` is a no-dependency script.

It checks:

- The expected skill and doc files exist
- Root skill links to every focused file
- Tracked text files do not contain home paths, emails, password-manager vault paths, PEM headers, or obvious token assignments

Run:

```bash
python3 tests/test_public_hygiene.py
```

## Integration / live CLI

Not in default CI. Live calls spend subscription quota and need local login.

When editing a focused skill, the author must run that CLI's `--help` and `--version` (or current official docs for OpenCode) and update the verified-version line.

A useful manual smoke test is a 20-line file-response call that writes a token such as `CLI_SMOKE_OK` to a result file. Do not commit the result.

## Why there is no e2e suite

The CLIs are proprietary, authenticated, and slow. A public GitHub Actions runner cannot log into Claude, Codex, Antigravity, or Grok. Encoding a fake subprocess would test the mock, not the vendor.

## Manual audit

Before publish or after a large edit:

```bash
rg -n "@|/Users/|BEGIN (RSA |OPENSSH )?PRIVATE KEY" --glob '!.git/**'
```

Every hit needs a human decision. Zero hits is not automatic proof of a complete review.
