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

### Before dispatch: progress and recovery

Before launching a long or file-producing CLI turn, the caller must define its supervision and recovery contract in the calling workflow:

- **Stage & Artifact**: Scope the turn to one bounded stage (for example, implementation, test execution, or review) and name the concrete artifact it must produce. For a conversational status query, define the returned evidence instead of inventing a disk artifact.
- **Task-Appropriate Budgets**: Set both an outer total deadline and an inspection or no-progress budget suited to the task. Timing thresholds belong in the caller workflow, not as a global minute limit across all CLIs.
- **Evidence Locations**: Specify where stdout, stderr, structured event logs, and any target result file are written so progress can be verified without guessing paths.
- **Owned Scope**: Track the exact attempt identity, session handle when available, and child processes owned by this invocation so recovery never collides with an active writer or unrelated process.
- **Stop & Recovery Action**: Decide in advance how to halt on deadline or failure, preserve logs and diffs, inspect partial artifacts, and narrow the next step. Bound retries and never repeat the same broad task without new evidence.

Distinguish actual phase progression from mere process liveness:

- **Phase progress vs. liveness**: A live PID, open transport, or repeated polling of an old subprocess is not task progress; verify that tool results and artifacts are advancing the current stage.
- **Buffered output vs. hang**: Quiet stdout or stderr may reflect stream buffering or a long tool step rather than a hung CLI. Use available structured events, same-run logs, or artifact activity before declaring a stall; log growth alone is not proof of useful progress.
- **Explicit failure**: A terminal command/test failure or broken prerequisite fails that stage even if the wrapper or a spawned child remains alive. Record it and choose a bounded recovery action. A recoverable warning or intermediate failed tool call does not by itself determine the entire CLI turn's final outcome; the acceptance gate still applies.

Respect the host environment's execution model:

- **No-polling contracts**: When the host requires native background completion notifications without parent-side progress checks, preserve that contract. The parent must not poll the child; an owning wrapper may use the bounded checkpoints below on its own child's structured stream, but must not turn them into a tight loop or a substitute for completion.
- **Stage splitting**: When mid-turn supervision is unavailable, split the work into shorter, independently verifiable stages before dispatch. Do not invent unsupported CLI callback flags, wakeup hooks, or background daemons.

#### Bounded progress checkpoints

The parent agent must wait for the host's native completion notification and must not poll the child. To observe progress during a run, the wrapper that owns the foreground CLI may read that CLI's structured event stream at coarse checkpoints (for example, every 30–60 seconds) to capture the session handle, detect early failure, and report stage changes.

A checkpoint is not a completion signal: it must not become a tight loop, duplicate or re-run the child's work, or treat log growth or a tool call as success. On clear failure, stop the turn and preserve the log, exit code, and partial artifacts for recovery. The main agent still receives completion through the normal background notification path.

### Wait Model & Process Lifetime

- **One-shot execution**: These foreground commands remain running until the turn completes. Wait for process completion within the supervision and recovery contract above; foreground semantics do not justify an oversized silent wait. This applies to `claude -p`, `codex exec`, `opencode run`, `agy --print`, `grok -p`, and `cursor agent -p`.
- **Live sessions**: Hold the input transport open and observe correlated events or bounded status reads. Assign the host an explicit lifecycle; a detached launcher exiting does not signal task completion.
- **Immediate-return commands**: Vendor slash commands that return immediately while spawning background workers (such as Grok `/deep-research`) do not represent finished turns; see [`grok_cli.md`](./grok_cli.md).

### Workspace Isolation, Instructions & Delegation Bounds

- **Workspace Root**: Start project work in the caller's actual workspace root and load its routed instruction files (such as `AGENTS.md` or `CLAUDE.md`). Preserve the requested model, language, and tool requirements. Do not silently substitute a stripped no-tools fixture for normal work.
- **Isolation Scope**: For isolated material transformations, run inside a scoped input directory. Note that sandbox flags constrain permissions but do not hide sibling files from model context.
- **Bounded Nesting**: Bound wrapper recursion. The standard architecture is one orchestrator plus one child CLI agent. Adding a third layer requires explicit operational justification.
- **Long Turns vs. Short Reads**: A long model turn may execute under a background worker process to keep the parent agent responsive. Conversely, short metadata lookups, `--help` inspections, and API reads do not require an intermediate model wrapper.
- **Direct Child Execution**: An SDK spawning its own Claude child process is executing directly, not delegating to another research agent.
- **Handoff Fidelity**: Retain original user feedback and source instructions intact in handoff files, and verify tangible output artifacts rather than accepting an unverified agent claim of completion.
