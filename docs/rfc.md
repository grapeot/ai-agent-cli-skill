# RFC: AI Agent CLI Skill

## Decision

Ship a public, filesystem-native skill pack with exactly one workspace-facing root entry point (`skills/skill_ai_agent_cli.md`). Maintain all vendor-focused skills and supporting reference documents inside the repository.

A consuming workspace integrates the pack by creating a single root symlink or a single root overlay (when local private policy is required). Workspaces must not create separate symlinks or private overlays for individual vendor sub-skills.

## Architecture & Modular Design

A single monolithic guide is unmaintainable across multiple rapidly evolving CLI tools. Vendor tools have distinct authentication lifecycles, permission models, and command-line structures. A modular hierarchy—comprising a lightweight router, vendor-specific operational guides, and deep protocol references—matches standard workspace skill discovery patterns.

- **Root Router (`skills/skill_ai_agent_cli.md`)**: Evaluates the task requirements, selects the appropriate vendor tool, and routes the agent to the matching focused skill. When accessed via a symlink, relative links resolve from the canonical root file's directory.
- **Focused Skills (`skills/<vendor>.md`)**: Detail exact command-line syntax, flag matrices, verification gates, and common operational pitfalls for that tool.
- **Internal References (`skills/references/<topic>.md`)**: Contain low-level protocol schemas and socket/HTTP interfaces loaded on demand by a focused skill.

## File-Response & Verification Contract

### One-Shot File Execution

File-producing tasks rely on three distinct filesystem artifacts:

1. **Prompt File**: A self-contained document containing complete instructions, context, schemas, and file paths.
2. **Result File**: The complete output artifact written directly to disk by the child process.
3. **Execution Logs**: Captured stdout, stderr, and vendor diagnostic files stored independently.

Standard output serves as an execution log, not the deliverable product. If the result file is absent or empty, the invocation is considered failed regardless of process exit status. Conversational status queries that do not request a file deliverable verify the returned text directly without inventing a placeholder file.

### Live Session Control

Live sessions follow an identity-and-event contract:
- The orchestrator maintains open transports and monitors streaming events or bounded status reads.
- Success requires correlating the submitted message UUID with a verified assistant response or tangible outcome. Process exit, socket writes, and HTTP 200 responses alone do not prove turn execution or completion.
- Session lifecycle states are kept strictly separate: an interrupt halts turn execution while preserving session state; it is not equivalent to process termination, server shutdown, or session archiving.

## Public / Private Separation

Public repository documents are restricted to:
- Official vendor documentation links and installation commands.
- Verified command-line flags and tested version metadata.
- Generic example paths (e.g., `/tmp/example-session/` or `$PWD/tmp/`).

Public documents must never contain:
- Machine-specific home directory paths or internal usernames.
- Real email addresses, phone numbers, or password-manager URI schemes.
- Unmasked API keys, session tokens, or private authorization headers.
- Private organizational workflows or proprietary subagent wrapping rules.

Workspaces requiring custom start directories, specific model preferences, or environment wrappers should define them in a local root overlay outside this repository.

## Vendor Interface Summaries

### Claude Code

Headless entry is `claude -p`. Flags and live-session capabilities were re-verified on CLI 2.1.299 and Agent SDK 0.3.299. Deep live-session protocols (inbox socket delivery, SDK-hosted Remote Control, and internal controller HTTP operations) are documented in `skills/references/claude_sessions.md`. Standard working sessions use the caller's workspace root, normal tools, and effective `auto` mode. Unsupported runtime APIs and internal controller routes are explicitly demarcated from public features.

### Codex

Headless execution uses `codex exec`. In CLI 0.156.1, flags `-a`, `--ask-for-approval`, and `--full-auto` are rejected. The documented non-interactive recipe uses `--sandbox` with `-c approval_policy="never"`, plus `-o` or `--output-schema` as needed. Custom OpenAI-compatible backends lacking the default web-search tool need the top-level string unit override `web_search = "disabled"` (not a boolean) in the configuration actually loaded.

### OpenCode

Headless execution uses `opencode run` directly. Running `opencode serve` with `--attach` is an optional optimization for persistent session reuse and cold-start minimization, not a mandatory prerequisite.

### Antigravity

Headless execution is invoked via `agy --print`. The `agy run` subcommand does not exist. Version 1.1.13 introduced `--output-format json|stream-json` and `--json-schema`, with a 5m print-timeout default in that version; later defaults differ. Use the focused skill's verification scope and set the execution timeout explicitly.

### Grok Build

Headless execution is provided by xAI's `grok -p` or `grok --prompt-file`, not the community `superagent-ai/grok-cli` or Groq. `grok agent` is the SDK/stdio transport, not the default automation entry. Passing `/deep-research` as a plain prompt terminates immediately because the background workflow is killed on exit; dispatch it via the in-turn `workflow` tool.

### Cursor

Headless execution uses `cursor agent -p`. CLI credentials reside in macOS Keychain independently of the Cursor IDE. Model speed options are specified via `-fast` model suffixes or bracket overrides (`[fast=true]`) rather than a standalone CLI flag.

## Testing Strategy

Automated CI runs `tests/test_public_hygiene.py` for file presence, root vendor coverage, version markers, and private-data patterns. Relative-link resolution is checked separately during review. Live vendor invocations are excluded from default CI; interface drift is verified using `--help` and `--version` when updating focused skills.

## Rejected Alternatives

- **Monolithic Single-File Guide**: Proven unmaintainable and prone to flag rot as individual CLIs update on divergent cadences.
- **Unified Python CLI Wrapper**: Introduces an unnecessary maintenance burden and wrapper abstractions without user demand.
- **Vendor-Specific Skill Packaging**: Limits cross-tool interoperability and locks workflows into vendor-specific distribution formats.
