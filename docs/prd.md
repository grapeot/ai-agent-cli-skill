# PRD: AI Agent CLI Skill

## Summary

Provide AI coding agents and automation scripts with a robust, verifiable contract for invoking external coding-agent CLIs and controlling existing Claude Code sessions. The skill pack itself is the deliverable: a single exposed root router, vendor-focused skills, and supporting internal references maintained directly within the repository.

## Problem

Calling raw model APIs is poorly suited for complex, multi-turn software engineering tasks. Raw API completions terminate prematurely, lack autonomous filesystem access, and omit tool-execution loops. While vendor coding CLIs solve these challenges, their command-line flags drift across releases, interactive terminal UIs fail in unattended subprocesses, and orchestrating models frequently hallucinate non-existent subcommands (such as `agy run`).

Earlier workspace documentation consolidated multiple tools into monolithic guides, mixed public instructions with private machine paths, and blurred the boundary between portable documentation and internal authoring conventions.

## Target Users

- **Delegating Agents**: Autonomous agents needing to dispatch complex research, refactoring, or code-generation tasks to a specialized CLI.
- **Automation Scripts**: Shell scripts and CI pipelines utilizing subscribed CLI capabilities without managing direct API keys.
- **Workspace Maintainers**: Developers integrating a clean, public skill contract while isolating private environment policies into local overlays.
- **Session Orchestrators**: Systems that need to discover, message, monitor, or interrupt running Claude Code sessions, including those linked to mobile devices via Remote Control.

## Success Criteria

1. **Deterministic Routing**: An agent reading only the root skill file can select the correct vendor CLI and identify the exact focused skill to load next.
2. **Definitive Completion Verification**: Each focused skill defines an unambiguous completion gate that does not depend on conversational stdout summaries.
3. **Filesystem Contract**: File-based prompt and result I/O is the default standard; command-line arguments are restricted to minimal driver prompts.
4. **Verified Interfaces**: Documented CLI flags match current production binaries; outdated or rejected arguments are explicitly removed.
5. **Public Hygiene**: The repository contains zero private home paths, employee credentials, personal emails, password-manager references, or internal hostnames.
6. **Single-Entry Exposure**: Workspaces install the pack by cloning the repository and exposing strictly the single root skill file to their global index.
7. **Identity-Preserving Live Control**: Live session operations correlate exact process IDs, message UUIDs, and cloud records, distinguishing transport delivery from execution, cancellation, and worker shutdown.
8. **Realistic Working Recipes**: Standard execution recipes load workspace context and tools under verified auto mode, treating stripped no-tools setups as testing fixtures rather than production defaults.

## Non-Goals

- Creating a new meta-wrapper binary, CLI daemon, or multi-vendor SDK.
- Replacing comprehensive official vendor documentation.
- Hardcoding workspace-specific directory layouts or private organizational workflows into public documentation.
- Guaranteeing underlying model reasoning accuracy, code correctness, or future vendor compatibility. The skill records version-scoped invocation and verification contracts.

## Scope

### In Scope

- Headless and non-interactive invocation of Claude Code, Codex, OpenCode, Antigravity, Grok Build, and Cursor.
- Shared file-response contract across all supported CLIs.
- Re-verified CLI flag matrices, default parameters, and known failure traps.
- Version-bounded Claude Code session discovery, peer inbox delivery, SDK hosting, Remote Control bridging, and controller HTTP operations.

### Out of Scope

- Interactive TUI usage, keyboard emulation, and terminal screenshot parsing.
- Vendor-specific custom packaging formats.
- Private workspace overlays, secrets management, and local machine configurations.
