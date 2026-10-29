# Grok native Imagine video

## Goal and verified scope

Produce a real Imagine `reference_to_video` clip through a Grok Build agent turn, recover the exact output, and validate the delivered media independently. This is an on-demand reference for [`grok_cli.md`](../grok_cli.md), not another globally exposed skill.

Verified on 2026-10-29: Grok Build 1.0.70 (`f50904eaee6c`) version/help/models and the installed `$HOME/.grok/bundled/skills/imagine/SKILL.md`. The tool contract below comes from that bundled skill, not a paid smoke test. Recovery and stream-selection pitfalls come from prior successful and failed generation runs. Recheck live help and the executing installation's bundled skill when they differ.

## Authorization, privacy, and availability

- Require explicit user authorization for paid image/video generation and its retry budget. A request to edit this skill, inspect help, or prepare a prompt does not authorize generation. Extra staging images are paid calls too. Do not substitute a slideshow, pan/zoom, or procedural animation for requested native generation.
- Confirm the intended credential/billing source and current login evidence without exposing credentials. A model list can appear while logged out; it does not establish authentication, entitlement, or price. API-key precedence was observed on 1.0.4; explicitly unset `XAI_API_KEY` for subscription-only execution rather than assuming the menu establishes billing.
- The bundled skill reports an upgrade notice on free/X Basic tiers. Relay an actual entitlement error and stop; do not retry, upgrade, or switch billing sources automatically.
- Under zero-data-retention (ZDR), the bundled skill says video storage fails unless a user-hosted bucket is configured. Preserve the actual tool error privately and stop. Do not disable privacy/ZDR, configure storage, or invent configuration keys. Those changes need separate explicit authorization. Old errors or saved config do not prove the current privacy state.
- Reference images and prompts go to the remote service. Use only inputs authorized for that purpose. Keep actual prompts, media, session IDs, signed URLs, account details, and raw tool errors in a caller-owned private/ignored task directory. Check ignore rules before staging anything; a directory name alone does not make it ignored. Public examples must remain synthetic.

## Invocation contract

`reference_to_video` is an **in-session tool**, not a verified `grok imagine` subcommand or a standalone JSON CLI endpoint. Ask the agent to read its bundled Imagine skill, inspect its available tool schema, invoke the tool, remain in the turn until it returns, and write both the clip and a status manifest. Do not select the Imagine model as the coding-agent `--model` to bypass the tool.

The bundled skill documents these inputs; the live tool schema remains authoritative:

| Input | Meaning / constraint |
|---|---|
| `prompt`, `aspect_ratio` | Required; set the ratio explicitly to match the source composition. The bundled video section does not enumerate allowed ratios, so do not import another image CLI's enum. |
| `first_frame`, `last_frame` | Pinned start/end images. One still can be animated with `first_frame` alone. Equal endpoints are a loop constraint, not proof of a seamless result. |
| `images` | Up to 14 conditioning references; these are re-rendered rather than literal timed frames. |
| `voices` | Up to 3 preset voice IDs, referenced as `<AUDIO_0>` etc.; only request speech when needed. |
| `keyframes` | Up to 4 `{image, timestamp_s}` anchors strictly inside the clip; times snap to a 1/3-second grid and anchors closer than 1/3 second are rejected. |
| `duration`, `resolution_name` | 1–15 seconds (default 6); `480p` or `720p`. These are requested settings; measure the actual file. |

At least one of `images`, `voices`, `first_frame`, `last_frame`, or `keyframes` is required. `<IMAGE_i>` indices follow upload order: `first_frame`, `images`, `keyframes`, `last_frame`. With a first frame, the first `images` reference is `<IMAGE_1>`. Pinned frames do not need prompt tags. Use authorized absolute file paths supported by the live schema; never invent filesystem paths for attachment tokens.

Example **prompt-file contents**, to adapt only after paid-call authorization (all paths are placeholders):

```text
Read your bundled Imagine skill and the live reference_to_video schema.
Generate exactly one native video using reference_to_video, with
first_frame and last_frame both /absolute/private-task/reference.png,
aspect_ratio 16:9, duration 8, resolution_name 720p.
Prompt: A locked camera observes a small abstract kinetic sculpture.
The base and frame stay fixed while the suspended ring rotates gently.
Do not generate images, spawn subagents, or make additional paid attempts.
Do not change privacy, ZDR, storage, login, or billing configuration.
If the tool returns an error or upgrade notice, preserve it and stop.
Wait for the tool to return. Copy its exact output to
/absolute/private-task/motion.mp4 without overwriting an existing file.
Write /absolute/private-task/video_result.json with actual tool/session
identity, source/output paths, requested settings, returned status/errors,
and whether generation and copying each completed. Unknown values are null.
Report the generated source path even if copying is denied; do not regenerate.
```

Launch shape, verified by 1.0.70 help:

```bash
env -u XAI_API_KEY grok --prompt-file /absolute/private-task/prompt.md \
  --cwd /absolute/private-task --permission-mode acceptEdits \
  --no-subagents --output-format json \
  > /absolute/private-task/stdout.json 2> /absolute/private-task/stderr.log
```

This example assumes subscription-only billing was selected. `acceptEdits` does **not** guarantee approval for shell copies or paid tools. Arrange narrowly scoped permissions using the installed CLI's actual rules before headless dispatch; do not add blanket `--always-approve` or bypass permissions to cure a denied copy. If required approval is unavailable, stop or recover the already generated file through the authorized caller. Define the outer deadline and evidence paths as in the root skill.

When multiple agents share a serial-only video queue, enforce it across all agents: agree on one shared exclusive lock, acquire with a bounded wait before generation, hold through tool completion/output capture, and release in `finally`. Per-agent sequential calls do not establish global serialization. Do not claim earlier unlocked calls complied retroactively.

## Output recovery and failure classification

Exit 0 is necessary for a successful invocation but insufficient: inspect stdout JSON and tool outcomes. `type: error`, an upgrade/storage error, or `stopReason: cancelled` is not success. A cancelled turn or denied `cp` can nevertheless leave a complete video; record invocation failure separately from recovered-artifact acceptance.

Use the exact session identity and generated path from this run's logs/tool response. Previously observed storage layout:

```text
$HOME/.grok/sessions/<urlencoded-cwd>/<session-id>/videos/<generated-file>.mp4
```

The cwd component encodes the absolute invocation directory, including slashes. Treat this as a recovery location to verify, not a guaranteed API: do not hardcode a session ID or `1.mp4`, scan unrelated sessions, or choose the newest file. Copy only a correlated output into the private task directory, preserving the original and existing deliverables. If correlation fails, report it rather than generating again. Store the original error and recovered path in the private manifest.

An observed 1.0.4 request failed with HTTP 426 demanding at least 1.0.13. Preserve the error and stop; inspect the current binary instead of changing skill text to pretend it upgraded. `grok update --stable` is supported by current help but mutates the installation and should run only within the caller's update authorization. No paid automatic retry follows an upgrade.

## Media and loop acceptance

Inspect streams before processing. Prior generated MP4s contained H.264 video, AAC audio, and an MJPEG attached cover; do not assume every run has that layout. After confirming `0:v:0` is the intended main H.264 stream, a silent copy can be made without re-encoding:

```bash
ffprobe -v error -show_streams -show_format -of json motion.mp4
ffmpeg -n -i motion.mp4 -map 0:v:0 -c:v copy -an -movflags +faststart silent.mp4
ffprobe -v error -show_streams -show_format -of json silent.mp4
ffmpeg -v error -i silent.mp4 -map 0:v:0 -f null -
```

If the main stream has another index, select that measured index. If its codec/container is unsuitable, choose and label an explicit transcode; stream copy does not convert codecs. The silent H.264 deliverable must have exactly one H.264 video stream, no audio or attached-picture stream, positive width/height/duration and a valid measured frame rate, and decode without errors. Compare actual dimensions, aspect, frame rate, and duration against the task's stated tolerances; never copy requested values into measured fields.

For loops, inspect actual first/last frames for geometry and brightness, sample consecutive frames through the clip for object drift, flicker and unexpected motion, and watch repeated playback across the join at delivery size. Matching endpoint images and contact sheets alone cannot prove temporal continuity. Judge framing/motion amplitude separately from the seam. Only label a loop seamless when these checks pass; otherwise state unverified or describe the visible defect. Crossfades/local repairs require re-encoding and honest labeling as post-processing; repeat media and loop checks afterward. Keep the native original.

The private `video_result.json` should distinguish `generation_completed`, `copy_completed`, invocation exit/status, actual tool name, session/source/delivered paths, requested settings, measured ffprobe fields, decode result, audio/cover presence, post-processing, and loop verdict with inspected evidence paths. Leave unexposed model IDs and other unknowns `null`. Deliver a native clip only after correlated provenance, media checks, and task-specific visual checks pass; recovered files do not turn a failed invocation into a successful one.
