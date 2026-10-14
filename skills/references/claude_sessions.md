# Claude Code Live Sessions and Remote Control

Repository-local reference, loaded on demand through `claude_code.md`. Do not expose this file through a separate workspace symlink or private overlay.

## Scope, Evidence, and Success

Verified on **2026-10-14**, macOS, Claude Code **2.1.299**, Agent SDK **0.3.299**:
- Exact local session discovery via registry and `agents --json`
- Local peer inbox message delivery and execution
- SDK-hosted Remote Control session continuity
- Internal controller HTTP endpoints: list, get, send, history, and user/assistant SSE streaming
- HTTP interrupt cancellation and state retention
- iOS-to-local round-trip UUID correlation
- Normal workspace tools (Bash, Read, Write) operating under effective auto mode with zero manual permission callbacks

Live tests were conducted on an explicitly authorized peer-accepting instance. Existing persistent-server workers have conditional source-level coverage rather than equivalent dynamic test coverage. Other versions, providers, or security policies require their own verification.

### Definition of Live Completion

Successful live delivery requires that the intended running object receives the message, executes the task, and produces a correlated response. If Remote Control is enabled, the corresponding cloud records must also be verified. When a deliverable file is requested, the output artifact must be independently validated on disk.

A socket write, HTTP 200, status notification, window title, launcher exit, or newly resumed copy does not satisfy this contract.

| Route | Interface Type & Operational Boundary |
|---|---|
| `claude agents --json` | Official local active-session listing. Does not mirror the mobile/cloud directory or provide recent message timestamps. |
| Per-session peer inbox | Officially documented for scripts and hooks. Minimum line-delimited JSON frame verified below. |
| SDK multi-turn input & `interrupt()` | Public interfaces bound to the process and transport currently held by the host, not an arbitrary live-process attach mechanism. |
| SDK `enableRemoteControl()` | Present and exercised in the 0.3.299 runtime, but absent from its public TypeScript declaration file (`.d.ts`). Version-dependent. |
| `--cloud <id> -p` | Official follow-up command for cloud sessions. Local bridge routing exists, though direct HTTP controller delivery was used in live experiments. |
| `/v1/code/sessions` controller | Internal, unsupported compatibility surface. Direct list, send, observe, and interrupt operations exercised with native login. |
| Daemon raw `reply` | Internal background-worker-map operation, not a general Remote API. An internal PTY fallback exists but is not recommended here. |

## Select and Discover the Existing Object

Use `claude agents --json` for a scriptable view of active local sessions; pass `--all` to include completed background sessions. The local directory may represent a superset of mobile sessions. Prioritize exact target correlation over identical list membership.

Output fields are conditional: `name`, `sessionId`, `pid`, `status`, and background `id`/`state` may not appear on every record. The `startedAt` field represents process startup time, not recent conversation activity. The `--cwd` filter is specific to background sessions, not a universal interactive scope.

Correlate the authorized target using its local UUID and live PID, verifying process start time where available. Inspect that specific target's registry file, normally located at `sessions/<pid>.json` under the active config root. Respect `CLAUDE_CONFIG_DIR` rather than assuming a default home directory. Verified registry fields include:
- `pid`
- `sessionId`
- `cwd`
- `version`
- `messagingSocketPath`
- `bridgeSessionId`
- `status`
- Update timestamps

Note that the CLI JSON listing does not necessarily expose the socket path or bridge session ID.

Registry reads can transiently encounter incomplete JSON during simultaneous updates. Implement a bounded retry on the exact same target record before flagging an error. Never treat a transient parse failure as justification to fork or resume a new conversation.

### Identifier Distinctions

| Identifier Type | Role & Valid Scope |
|---|---|
| Local UUID | Conversation and transcript identity on disk; used for stopped-session resumption. |
| Background handle | Supervisor-managed handle for attach, logs, and stop commands. May derive from a UUID but requires separate identity validation. |
| Cloud `session_…` / `cse_…` | Code controller and Remote Control URL identity. Cloud compatibility paths translate between these two prefixes. |

Never attempt to derive a cloud session ID from a local UUID through prefix substitution or string truncation. Direct associations are available in registry metadata and local transcript `type: "bridge-session"` records (`sessionId`, `bridgeSessionId`, `lastSequenceNum`), as well as the current host's bridge response.

A workspace's `bridge-pointer.json` file assists server and directory restoration; it is not a global UUID lookup database. A cleared or stale record alone proves neither a current connection nor its absence.

When reading local history via SDK methods (`getSessionInfo`, `getSessionMessages`), use the actual stored transcript scope. **The current working directory and transcript project key can diverge after session resumption.** In verified testing, a root-scoped history lookup returned zero messages while the original storage scope contained the current active turn. Query the recorded storage association rather than searching unrelated history or instantiating a replacement session.

## Deliver Through the Local Peer Inbox

On macOS and Linux, a session with messaging enabled can publish its Unix domain socket path in `CLAUDE_CODE_MESSAGING_SOCKET`; the registry may expose `messagingSocketPath`. Confirm the selected live object's ownership before connecting. Windows uses a named pipe with distinct authentication requirements.

The verified minimum business frame is a single UTF-8 JSON line:

```json
{"type":"user","uuid":"<unique-message-uuid>","session_id":"<target-local-uuid>","message":{"role":"user","content":"<authorized task>"}}
```

Requirements and boundaries:
- `message.content` must be a non-empty **string**. Do not pass an array of content blocks.
- `uuid` and `session_id` are optional in the current handler. When `session_id` is supplied, it must match the process's current local UUID, not a cloud session ID.
- Terminate the frame with a newline (`\n`).

### Minimal Node.js Socket Delivery

This helper sends a task to an already-running process without creating a new Claude session:

```js
import net from 'node:net';
import { randomUUID } from 'node:crypto';

// Parameters must identify an exact verified target.
const inbox = process.env.TARGET_INBOX;
const localId = process.env.TARGET_LOCAL_ID;
const task = process.env.TASK_TEXT;
if (!inbox || !localId || !task?.trim()) {
  throw new Error('Exact target inbox, local UUID, and non-empty task required');
}

const socket = net.createConnection(inbox);
const deadline = setTimeout(() => socket.destroy(), 1000);

socket.on('connect', () => {
  const payload = {
    type: 'user',
    uuid: randomUUID(),
    session_id: localId,
    message: { role: 'user', content: task }
  };
  socket.write(JSON.stringify(payload) + '\n');
});

socket.on('close', () => clearTimeout(deadline));
socket.on('error', error => {
  console.error(error.message);
  process.exitCode = 1;
});
// The one-second connection window and socket close prove neither delivery nor execution.
// Independently observe the transcript or task outcome before sending further input.
```

### Inbound Policy & Authentication

Messages sent via this socket are classified as **peer** input. The session's `crossSessionInbound` setting dictates whether input is accepted, held for review, or refused:
- Running under the same OS user account does not grant an external script child-process or human-controller status.
- Do not attempt to bypass gates by spoofing client platforms, forging sender permissions, or reusing internal child tokens.
- Configure `crossSessionInbound: 'accept'` only when peer control has been authorized for that specific instance; do not change unrelated sessions or global policy.
- On macOS and Linux, the initial authentication line is optional. On Windows, an initial `{"type":"auth","token":"<session-token>"}` frame is required.
- The session closes connections that remain idle without completing a frame within 30 seconds.
- Do not infer message delivery from application ACKs. Verified live experiments received no application ACK over the socket, yet execution proceeded and was confirmed through output artifacts.
- When the receiver is idle, peer delivery initiates a new turn. When the receiver is busy running tools, peer messages are queued and processed between tool executions; delivery does not interrupt the active tool.

## Provision a Normal Working Session

This workflow provisions an owned child process. It is not an attach-by-UUID API for pre-existing external processes.

Start from the caller's actual workspace root and load its standard instruction files. SDK defaults differ significantly from standard CLI behavior. The verified working configuration is:

```js
const options = {
  cwd: workspaceRoot,
  systemPrompt: { type: 'preset', preset: 'claude_code' },
  settingSources: ['user', 'project', 'local'],
  permissionMode: 'auto',
  // Only when peer control is explicitly authorized for this instance:
  settings: { crossSessionInbound: 'accept' }
};
// Use default tools for normal operations.
// Avoid setting tools: [] or strict empty MCP configurations for production work.
// const q = query({ prompt: longLivedInput, options });
```

Operational guidance:
- Maintain an open `AsyncIterable<SDKUserMessage>` stream and process the Query's event output. Keep the hosting process alive.
- The equivalent bidirectional CLI command is `-p --input-format stream-json --output-format stream-json --verbose`.
- Supplying a `session_id` in JSON input does not route messages across independent processes via stdin.
- Verify **effective** initialization parameters: confirm `init.permissionMode` resolves to `auto`, verify the working directory, and validate actual tool execution. In verified testing, Bash retrieved `pwd` and system time, Write generated a probe artifact, and Read verified it, all without manual confirmation prompts.
- `auto` mode is an active risk evaluation model, not an unconditional bypass or an always-allow callback. Surface unresolved authorization prompts to an authorized host or user interface.
- Setting `tools: []` is an isolation test fixture, not a production configuration. In testing, built-in tools were disabled but cloud account MCP tools still appeared until isolated with a strict empty MCP configuration. Neither restriction belongs in standard development setups.

## Enable Remote Without Replacing the Conversation

Remote Control requires an eligible, full-scope native claude.ai login and active feature evaluation. Standard API keys cannot authenticate Remote Control sessions.
- Do not inject native OAuth tokens into `CLAUDE_CODE_OAUTH_TOKEN` under the assumption of identical Remote eligibility; token inference modes are distinct.
- Use the native credential store for standard workflows.
- `--bare` disables keychain lookups, context loading, and the default inbox, making it unsuitable for Remote Control.
- Do not disable required feature evaluation flags. In testing, setting `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` combined with an environment OAuth token triggered generic Remote initialization failures. Restoring native login and removing the traffic restriction resolved the issue (individual contributions were not isolated). Settings such as `DISABLE_TELEMETRY`, `DO_NOT_TRACK`, or `DISABLE_GROWTHBOOK` can similarly affect evaluation; inspect runtime diagnostics directly.

### SDK Remote Control API

In SDK 0.3.299, the Query instance exposes the method at runtime, although it is omitted from the public `.d.ts` declaration file:

```js
if (typeof q.enableRemoteControl !== 'function') {
  throw new Error('SDK runtime does not expose enableRemoteControl');
}
const bridge = await q.enableRemoteControl(true, displayName, {
  keepSessionOnExit: true
});
// Treat session_url and bridge_session_id as sensitive metadata.
// Keep consuming q; do not terminate the Query loop after the initial turn.
```

### Resuming Stopped Sessions vs. Active Sessions

When restoring a **stopped** owned session, SDK `resume` can preserve the local UUID while assigning a new PID. Re-establishing a recorded bridge uses `reattachSessionId: originalCloudId`, followed by verification of the returned ID and registry state. Never accept a newly minted cloud ID as session continuity.

Tested strict reattachment in 2.1.299 used the internal instance-scoped `CLAUDE_BRIDGE_REATTACH_SESSION` mechanism for reattach-or-fail behavior. This is an internal version-dependent implementation, not a stable public setting. Establish a no-replacement guarantee before attempting continuity; do not discover afterward that the attempt created another cloud conversation.

Operational boundaries:
- `claude --remote-control` runs an interactive local session. `claude remote-control` launches a persistent server process that manages worker sessions; `--spawn=same-dir/worktree/session` governs worker scoping.
- Running `remote-control --session-id` expects a remote Code URL ID, not a local transcript UUID, and controls server lifecycle rather than appending messages.
- Using `--bg --resume` on an active session can spawn a duplicate conversation. While running-background resume can send and attach in CLI 2.1.285+, TTY and flag constraints make it unsuitable as a general headless append interface.
- Desktop Chat, Desktop Code, Cowork, SDK-hosted Remote, and cloud-hosted Code are distinct session identities. Sharing an underlying account does not unify session scopes.
- Interactive processes can switch local conversations while preserving an existing Remote connection and its original title. Never rely solely on window titles for target identification.
- `DirectConnectTransport` issues `POST /sessions` on initialization and may execute `DELETE` upon closing; it is not a safe read-only attach probe for arbitrary Remote URLs.
- Provide explicit host lifetimes. The `keepSessionOnExit` option is a retention request, not a guarantee of permanent hosting. Never shut down a shared server to clean up an individual conversation.

## Internal Controller HTTP: List, Send, Observe, Interrupt

The tested product controller endpoint is `https://api.anthropic.com/v1/code/sessions`. This is an internal, unsupported compatibility surface.
- Credentials must be retrieved in memory from an approved native credential provider. Never pass tokens via argv, commit them to disk, or log them. Do not attempt automated token rotation across external processes.
- Request headers vary by endpoint: OAuth Bearer, `anthropic-version`, client platform, and conditional organization, trusted-device, or attestation headers. Start with current Code client behavior rather than legacy beta header sets.
- Tested calls used the honest `claude_code_cli` client platform with an instance configured to accept peer input.

| Operation | Method & Route Pattern |
|---|---|
| Directory | `GET /v1/code/sessions?limit=100`, page using `cursor=<next_cursor>` until exhausted |
| Exact Metadata | `GET /v1/code/sessions/<cloud-id>`; the tested response wrapped metadata in `response_shape` |
| History | `GET /v1/code/sessions/<cloud-id>/events` |
| Stream | `GET /v1/code/sessions/<cloud-id>/events/stream?from_sequence_num=<baseline-seq>` |
| Send Event | `POST /v1/code/sessions/<cloud-id>/events` with event wrapper |
| Interrupt | `POST /v1/code/sessions/<cloud-id>/events` with `control_request` wrapper |

Directory listings must include entries where `environment_kind: bridge`. Internal helper utilities may filter by title, exclude bridge sessions, or truncate paginated results; do not rely on them for complete inventories. The `last_event_at` timestamp tracks recent event activity (which `updated_at` may mirror) rather than the most recent human message. Sort records explicitly and handle missing timestamps gracefully.

### Event Submission

The verified event submission envelope is below. Some native callers omit the outer `session_id`, so this is not a claim that the server accepts only one body form:

```js
const userEvent = {
  type: 'user',
  uuid: messageUuid,
  session_id: cloudId,
  parent_tool_use_id: null,
  message: { role: 'user', content: taskText }
};
const body = { session_id: cloudId, events: [{ payload: userEvent }] };
// POST the body once with approved in-memory headers.
```

- Capture the baseline sequence number **before** dispatching the event.
- Fix a single message UUID. If a network timeout or ambiguous status occurs, query the event log for that specific UUID before retrying. Generating a new UUID produces a duplicate turn rather than an idempotent retry.
- In verified tests, assistant response UUIDs matched across local and cloud views, and Remote inbox input preserved `origin.kind: peer`.
- iOS client input may omit the inner `session_id`. Destination endpoint validation and UUID correlation confirmed successful delivery; the absence of `session_id` inside the event payload does not imply failure.

### Interrupt Execution

The tested HTTP interrupt payload is:

```js
const interruptEvent = {
  type: 'control_request',
  uuid: controlEventUuid,
  request_id: controlRequestId,
  session_id: cloudId,
  request: { subtype: 'interrupt' }
};
// Transmitted via the same events wrapper. Correlate with control_response.response.request_id.
```

Verification requires confirming that a turn was actively executing, matching the `control_response` with the original `request_id`, ensuring execution was halted, and verifying the session remains in an operational retained state. Worker termination, server shutdown, or conversation archiving are distinct operations. Queued messages or background work may still remain after an interrupt.

### Streaming and Lifecycle Observations

SSE streaming experiments observed user and assistant events, but did not certify complete multi-event result streams. The stream observer encountered body-read hangs during connection termination. Always configure explicit read timeouts, close network readers deliberately, and reconcile conversation state using finite `GET /events` queries. Do not assume production-grade continuous observation or unbounded history replay.

Do not confuse controller endpoints with worker infrastructure (`/worker/events`, `/worker/events/stream`, worker registration, or epoch leases). Public Managed Agents (`/v1/sessions`) and legacy CCR share similar path conventions but operate under different authentication and session lifecycles. Never register replacement worker processes to deliver user messages.

## Official Sources

- [Claude Code CLI Reference](https://code.claude.com/docs/en/cli-reference)
- [Cross-Session Messaging & Script Inbox](https://code.claude.com/docs/en/cross-session-messaging#the-sessions-inbox-socket)
- [Remote Control Documentation](https://code.claude.com/docs/en/remote-control)
- [Agent View & Background Sessions](https://code.claude.com/docs/en/agent-view)
- [Local Session Resumption](https://code.claude.com/docs/en/sessions)
- [Official Cloud CLI Follow-Ups](https://code.claude.com/docs/en/claude-code-on-the-web#send-follow-ups-from-the-cli)
- [Claude Agent SDK TypeScript](https://code.claude.com/docs/en/agent-sdk/typescript)
- [Agent SDK 0.3.299 Runtime](https://unpkg.com/@anthropic-ai/claude-agent-sdk@0.3.299/sdk.mjs) and [Public Types](https://unpkg.com/@anthropic-ai/claude-agent-sdk@0.3.299/sdk.d.ts)
- [SDK-Hosted Remote Control Feature Request](https://github.com/anthropics/claude-agent-sdk-typescript/issues/460) (community reference, not an official compatibility contract)
