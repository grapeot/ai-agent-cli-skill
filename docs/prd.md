# PRD: AI Agent CLI Skill

## Summary

Give an AI coding agent a reliable way to call another coding-agent CLI. The skill pack is the product: one root router plus one focused file per vendor CLI.

## Problem

Calling a raw model API is a poor fit for long, tool-using work. The model stops early, cannot see the filesystem, and has no loop. Vendor CLIs already solve that, but their flags drift, their interactive TUIs are useless in a subprocess, and agents routinely invent commands such as `agy run`.

The older workspace guide mixed five tools in one file and then split only some of them. Codex stayed inside the overview. Private paths and writing-workflow policy leaked into the same documents that should be publishable.

## Users

- An agent that needs to delegate a long research, rewrite, or file-edit task
- A human writing a script that must call a subscribed CLI instead of an API key
- A workspace maintainer who wants one public contract plus a private overlay

## Success criteria

1. A new agent that reads only the root skill can choose a CLI and name the focused file it must load next.
2. Each focused skill states a completion check that does not depend on a chatty stdout summary.
3. File-based I/O is the default. Prompt text in argv is allowed only for short driver prompts.
4. Flag tables match the verified binary, including removals. A rejected flag is a skill bug.
5. The public repo contains no private emails, home paths, vault references, or internal hosts.
6. A workspace can install the pack by handing the GitHub URL to a coding agent and exposing only the root skill.

## Non-goals

- A new wrapper CLI or SDK
- Replacing vendor docs
- Encoding one workspace's directory layout or writing workflow as if it were universal
- Guaranteeing model quality. The skill guarantees invocation shape and completion checks.

## Scope

In:

- Claude Code, Codex, OpenCode, Antigravity, Grok Build
- Non-interactive / headless invocation
- Shared file-response contract
- Verified flags and known traps

Out:

- Interactive TUI usage except as a negative example
- Vendor-specific skill packaging formats
- Private overlays (those live in the consuming workspace)
