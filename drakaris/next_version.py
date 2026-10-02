#!/usr/bin/env python3
"""Resolve a próxima tag Docker do drakaris (vX.Y).

Cada `drakaris` incrementa. Tag fixa só se a mensagem pedir
(`drakaris v1.5` / `drakaris versão 2.0`). Sem histórico → v1.0.
`latest` é tag extra, não entra na sequência.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

VERSION_RE = re.compile(r"^v?(\d+(?:\.\d+)*)$")
IMAGE_TAG_RE = re.compile(
    r"image:\s*['\"]?([^\s'\"#]+)",
    re.IGNORECASE,
)
PIN_VERSAO_RE = re.compile(
    r"(?i)(?:vers[aã]o|version)\s+v?(\d+(?:\.\d+)*)"
)
PIN_DRAKARIS_RE = re.compile(r"(?i)drakaris\s+v(\d+(?:\.\d+)*)")
EXAMPLE_RE = re.compile(
    r"(?i)(?:exemplo|example)\s*:.*?(?=\n|$)",
    re.DOTALL,
)
SKIP_DIR_NAMES = {".git", ".github", "node_modules", ".venv", "venv", "__pycache__"}


def normalize(tag: str) -> str:
    raw = tag.strip()
    if raw.lower() in {"latest", "stable", "main", "dev"}:
        raise ValueError(tag)
    match = VERSION_RE.match(raw)
    if not match:
        raise ValueError(tag)
    return "v" + match.group(1)


def parse_tuple(tag: str) -> tuple[int, ...]:
    return tuple(int(p) for p in normalize(tag)[1:].split("."))


def increment_version(tag: str) -> str:
    parts = list(parse_tuple(tag))
    if len(parts) == 1:
        parts.append(1)
        return "v" + ".".join(str(p) for p in parts)
    parts[-1] += 1
    return "v" + ".".join(str(p) for p in parts)


def parse_requested_version(message: str) -> str | None:
    stripped = EXAMPLE_RE.sub("", message or "")
    match = PIN_VERSAO_RE.search(stripped)
    if match:
        return normalize(match.group(1))
    match = PIN_DRAKARIS_RE.search(stripped)
    if match:
        return normalize(match.group(1))
    return None


def _tag_from_image(value: str) -> str | None:
    image = value.strip().strip("'\"")
    if not image or image.startswith("${"):
        return None
    # registry:port/name:tag — tag is after the last colon that isn't a port-only hint
    if "/" in image:
        name = image.rsplit("/", 1)[-1]
    else:
        name = image
    if ":" not in name:
        return None
    tag = name.rsplit(":", 1)[-1]
    if "@" in tag:
        tag = tag.split("@", 1)[0]
    try:
        return normalize(tag)
    except ValueError:
        return None


def _is_ours(image_line: str) -> bool:
    return "kiwel/" in image_line.lower()


def find_current_version(repo: Path) -> str | None:
    version_file = repo / "VERSION"
    if version_file.is_file():
        raw = version_file.read_text(encoding="utf-8").splitlines()
        if raw and raw[0].strip():
            return normalize(raw[0])

    ours: list[str] = []
    for path in repo.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".yaml", ".yml"}:
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for match in IMAGE_TAG_RE.finditer(text):
            if not (_is_ours(match.group(0)) or _is_ours(match.group(1))):
                continue
            tag = _tag_from_image(match.group(1))
            if tag:
                ours.append(tag)
    if not ours:
        return None
    return max(ours, key=parse_tuple)


def resolve_next(
    repo: Path,
    message: str,
    write: bool = False,
    current: str | None = None,
) -> str:
    pinned = parse_requested_version(message)
    if pinned:
        nxt = pinned
    else:
        found = find_current_version(repo)
        if found is None and current:
            found = normalize(current)
        nxt = "v1.0" if found is None else increment_version(found)
    if write:
        (repo / "VERSION").write_text(nxt + "\n", encoding="utf-8")
    return nxt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Próxima tag Docker do drakaris")
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--message", default="")
    parser.add_argument("--current", default=None, help="Tag ao vivo se o repo não tiver VERSION")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    repo = args.repo.expanduser().resolve()
    try:
        tag = resolve_next(repo, args.message, write=args.write, current=args.current)
    except ValueError as exc:
        print(f"versão inválida: {exc}", file=sys.stderr)
        return 1
    print(tag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
