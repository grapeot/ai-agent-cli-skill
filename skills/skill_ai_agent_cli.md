---
name: ai-agent-cli
description: >-
  Routes agents to non-interactive coding-agent CLIs and live Claude Code
  session control. Use when calling Claude Code, Codex, OpenCode, Antigravity,
  Grok Build, or Cursor; discovering or messaging an existing Claude session;
  connecting it to Remote Control; or observing and interrupting work.
---

# AI Agent CLI

## Metadata

- **Type**: Router / BestPractice
- **Role**: Root skill for vendor coding-agent CLI orchestration
- **Scope**: Expose only this root file in a workspace skill index. Focused skills and references remain inside this repository; do not create separate global symlinks or private overlays for individual sub-skills.

## Goal & Boundaries

### Goal

Route execution to the appropriate vendor CLI or existing live session, preserving the requested workspace root, model, permissions, conversation identity, and verifiable task outcomes. File-producing work follows the file-response contract; live session control follows the identity-and-event contract below.

### When to Use

Use a CLI agent when at least one condition holds:
- The task requires multiple tool calls or several minutes of autonomous execution.
- The child process must read and write local files in the workspace.
- You want to use subscription quota instead of raw API credits.
- You need an auditable trail of disk modifications and tool calls.
- You need to discover, message, observe, interrupt, or connect an existing Claude Code session to Remote Control.

### Boundaries & Out of Scope

- **In-process threshold**: Do not invoke a CLI agent for a single short completion doable in-process.
- **Interactive interfaces**: Interactive TUIs, keyboard emulation, and screenshot automation are out of scope. Documented programmatic inboxes and explicitly labeled internal protocols are separate capabilities.
- **Invented commands**: Subcommands like `agy run`, `claude exec`, or `grok print` do not exist and are prohibited.
- **Subagent distinction**: Do not treat a same-brand model subagent as the vendor CLI binary.
- **Hygiene & privacy**: Never commit prompt files, result files, or session logs containing task text or account credentials.

## Focused Skills & Routing

Load this root file first. Load exactly one vendor-focused file before constructing a command; that file may request an on-demand internal reference from this repository.

If this root file is exposed through a symlink, resolve its canonical path first. Always resolve relative links below against the canonical file's directory, not the workspace alias directory. Do not create sub-skill symlinks to repair relative paths. A workspace-specific root overlay, if genuinely needed, must name this canonical root and resolve relative links from this directory.

| CLI | Command | Focused Skill | Primary Preference / Fit |
|---|---|---|---|
| Claude Code | `claude -p`; SDK; existing-session inbox/controller | [`claude_code.md`](./claude_code.md) | One-shot tasks, tools with auto mode, live sessions, and Remote Control |
| Codex | `codex exec` | [`codex_cli.md`](./codex_cli.md) | Structured last-message / JSON Schema automation |
| OpenCode | `opencode run` | [`opencode_cli.md`](./opencode_cli.md) | Provider-agnostic model choice, or an HTTP server |
| Antigravity | `agy --print` | [`antigravity_cli.md`](./antigravity_cli.md) | Gemini models via an Antigravity subscription |
| Grok Build | `grok -p` / `grok --prompt-file` | [`grok_cli.md`](./grok_cli.md) | Grok models via an xAI / SuperGrok subscription |
| Cursor | `cursor agent -p` | [`cursor_cli.md`](./cursor_cli.md) | Cursor-hosted model menu (Composer, Gemini Flash, etc.) via a Cursor subscription |

Preferences are starting heuristics, not rigid rankings. If the user or task specifies a CLI, use that one.

## Acceptance Criteria

### One-Shot Invocations

A one-shot invocation succeeds only when all applicable conditions are satisfied:

1. **Process Exit**: The child process exits cleanly with code 0.
2. **Artifact Verification**: When a result file is requested, it exists, is non-empty, and satisfies all task-specific hard checks (tokens, schema, required URLs). A fluent stdout summary is not a fallback product. If the task is a conversational status request with no requested file, verify the actual response rather than inventing a file deliverable.
3. **Execution Auditability**: The wrapper must verify and record:
   - The exact command line executed
   - Resolved paths for prompt file, result file, and log outputs
   - Process exit code
   - Concrete evidence that any requested result file was read back from disk

### Live Session Operations

Live session control follows an identity-and-event contract rather than process termination:

1. **Exact Object Continuity**: Resolve the intended running object by correlating its local session ID, live PID, and remote ID when applicable. Never substitute an active conversation with a newly resumed copy.
2. **Correlated Message & Outcome**: Correlate the submitted message UUID with an actual assistant response or concrete task outcome. A socket write, HTTP 200, status notification, window title, or transport ACK alone does not constitute task execution.
3. **Preserved Process Lifetime**: Maintain the live process and held transport when continued interaction is requested; process exit is not a requirement for success. Verify requested file artifacts in addition to turn completion.
4. **Remote Verification**: For Remote Control, verify the corresponding cloud events and status records. Distinguish backend synchronization from an end-user's mobile UI interaction.
5. **Distinct Control States**: For interrupts, verify cancellation of the running turn and the object's retained state. Do not substitute worker shutdown, process termination, or conversation archive for an interrupt.

## Enabling Guidance & Execution Contract

### File-Response Contract

File-producing tasks and long content processing must use filesystem artifacts:
- Write the full task instruction to a prompt file. Keep the command-line driver prompt brief (for example: `"Read /path/to/prompt.md and follow it exactly."`).
- Instruct the child CLI to write its complete deliverable directly to a designated result file path.
- Capture stdout, stderr, and vendor log files separately for debugging and auditability.
- Clean NUL characters out of prompt strings (`replace('\0', '')`) before passing them to subprocesses.
- In-memory messages are reserved for short status queries, live message delivery, and streaming event callbacks. Keep private task text, raw transcripts, and authentication material out of public examples and persistent logs.

### Wait Model & Process Lifetime

- **One-shot execution**: Wait for process completion. Tools such as `claude -p`, `codex exec`, `opencode run`, `agy --print`, `grok -p`, and `cursor agent -p` remain running until the turn completes. Configure the wrapper timeout accordingly.
- **Live sessions**: Hold the input transport open and observe correlated events or bounded status reads. Assign the host an explicit lifecycle; a detached launcher exiting does not signal task completion.
- **Immediate-return commands**: Vendor slash commands that return immediately while spawning background workers (such as Grok `/deep-research`) do not represent finished turns; see [`grok_cli.md`](./grok_cli.md).

### Workspace Isolation, Instructions & Delegation Bounds

- **Workspace Root**: Start project work in the caller's actual workspace root and load its routed instruction files (such as `AGENTS.md` or `CLAUDE.md`). Preserve the requested model, language, and tool requirements. Do not silently substitute a stripped no-tools fixture for normal work.
- **Isolation Scope**: For isolated material transformations, run inside a scoped input directory. Note that sandbox flags constrain permissions but do not hide sibling files from model context.
- **Bounded Nesting**: Bound wrapper recursion. The standard architecture is one orchestrator plus one child CLI agent. Adding a third layer requires explicit operational justification.
- **Long Turns vs. Short Reads**: A long model turn may execute under a background worker process to keep the parent agent responsive. Conversely, short metadata lookups, `--help` inspections, and API reads do not require an intermediate model wrapper.
- **Direct Child Execution**: An SDK spawning its own Claude child process is executing directly, not delegating to another research agent.
- **Handoff Fidelity**: Retain original user feedback and source instructions intact in handoff files, and verify tangible output artifacts rather than accepting an unverified agent claim of completion.
