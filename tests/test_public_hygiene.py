#!/usr/bin/env python3
"""Offline checks for repo shape and public-repo hygiene."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "LICENSE",
    ".gitignore",
    ".env.example",
    "docs/prd.md",
    "docs/rfc.md",
    "docs/working.md",
    "docs/test.md",
    "skills/skill_ai_agent_cli.md",
    "skills/claude_code.md",
    "skills/codex_cli.md",
    "skills/opencode_cli.md",
    "skills/antigravity_cli.md",
    "skills/grok_cli.md",
    ".github/workflows/ci.yml",
]

FOCUSED = [
    "claude_code.md",
    "codex_cli.md",
    "opencode_cli.md",
    "antigravity_cli.md",
    "grok_cli.md",
]

SKIP_DIR_NAMES = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}
TEXT_SUFFIXES = {".md", ".yml", ".yaml", ".py", ".toml", ".txt", ".example", ".gitignore"}

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
ALLOWED_EMAILS = {"alice@example.com", "bob@example.net"}
HOME_PATH_RE = re.compile(r"/Users/[A-Za-z0-9._-]+")
OP_RE = re.compile("op" + "://")
PEM_RE = re.compile(r"BEGIN (RSA |OPENSSH )?PRIVATE KEY")
ASSIGNED_SECRET_RE = re.compile(
    r"(?i)\b(api[_-]?key|token|password|secret)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-/+]{12,}"
)
PRIVATE_HOST_RE = re.compile(r"\b(yage\.ai|superlinear\.academy|" + "grapeot@" + ")")


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {".gitignore", ".env.example"}:
            files.append(path)
    return files


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"missing required file: {rel}")

    root_skill = (ROOT / "skills/skill_ai_agent_cli.md").read_text(encoding="utf-8")
    for name in FOCUSED:
        if name not in root_skill:
            errors.append(f"root skill does not mention {name}")
        body = (ROOT / "skills" / name).read_text(encoding="utf-8")
        if "Verified" not in body and "verified" not in body and "official CLI docs" not in body:
            errors.append(f"{name} has no verified-version marker")

    for path in iter_text_files():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in EMAIL_RE.findall(text):
            if match.lower() not in {item.lower() for item in ALLOWED_EMAILS} and not match.lower().endswith(
                "@example.com"
            ) and not match.lower().endswith("@example.net"):
                errors.append(f"{rel}: email {match}")
        if HOME_PATH_RE.search(text):
            errors.append(f"{rel}: machine home path")
        if OP_RE.search(text):
            errors.append(f"{rel}: op:// reference")
        if PEM_RE.search(text):
            errors.append(f"{rel}: PEM private key header")
        if PRIVATE_HOST_RE.search(text):
            errors.append(f"{rel}: private host or handle")
        for match in ASSIGNED_SECRET_RE.finditer(text):
            value = match.group(0)
            if "replace-with-your-real-key" in value or "example" in value.lower():
                continue
            errors.append(f"{rel}: possible secret assignment: {value[:80]}")

    if errors:
        print("FAIL")
        for item in errors:
            print(f"  - {item}")
        return 1
    print(f"PASS ({len(REQUIRED_FILES)} required files, {len(iter_text_files())} text files scanned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
