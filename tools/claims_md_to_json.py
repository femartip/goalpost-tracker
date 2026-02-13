#!/usr/bin/env python3
"""Convert data/claims.edit.md -> data/claims.json

This is a tiny purpose-built parser for the repo's YAML-ish format.
It supports:
- flat keys: id, tweetUrl, author, tweetDate, status, achievedDate, claimType, lastChecked
- taxonomy: domain, modality, topic list
- block scalars: claimText, notes, assessment
- evidence list: - url/title/date?/notes (notes is a block scalar)

Usage:
  python3 tools/claims_md_to_json.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INP = ROOT / "data" / "claims.edit.md"
OUT = ROOT / "data" / "claims.json"


def strip_comment(v: str) -> str:
    # remove inline comments that start with two spaces + # (our style)
    if "  #" in v:
        v = v.split("  #", 1)[0]
    return v.strip()


def parse_block(lines: list[str], i: int, indent: int) -> tuple[str, int]:
    # parse indented block (|) where content lines start with `indent` spaces
    buf: list[str] = []
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            buf.append("")
            i += 1
            continue
        if len(line) - len(line.lstrip(" ")) < indent:
            break
        buf.append(line[indent:])
        i += 1
    # rstrip but keep internal newlines
    return "\n".join(buf).rstrip(), i


def main() -> int:
    raw = INP.read_text(encoding="utf-8")
    lines = raw.splitlines()

    claims: list[dict] = []
    i = 0

    def new_claim() -> dict:
        return {
            "id": "",
            "tweetUrl": "",
            "author": "",
            "tweetDate": "",
            "status": "ambiguous",
            "achievedDate": "",
            "claimType": "other",
            "taxonomy": {"domain": "other", "modality": "other", "topic": []},
            "lastChecked": "",
            "claimText": "",
            "notes": "",
            "assessment": "",
            "evidence": [],
        }

    current: dict | None = None

    while i < len(lines):
        line = lines[i]
        if line.strip() == "---":
            if current and current.get("id"):
                claims.append(current)
            current = new_claim()
            i += 1
            continue

        if current is None:
            i += 1
            continue

        if line.strip() == "" or line.lstrip().startswith("#"):
            i += 1
            continue

        if ":" in line and not line.startswith("  -") and not line.startswith("    "):
            key, rest = line.split(":", 1)
            key = key.strip()
            rest = rest.lstrip()

            if rest == "|":
                val, i = parse_block(lines, i + 1, indent=2)
                current[key] = val
                continue

            if key == "taxonomy":
                i += 1
                # parse taxonomy block
                while i < len(lines):
                    l2 = lines[i]
                    if l2.strip() == "" :
                        i += 1
                        continue
                    if len(l2) - len(l2.lstrip(" ")) < 2:
                        break
                    if l2.strip().startswith("domain:"):
                        current["taxonomy"]["domain"] = strip_comment(l2.split(":",1)[1])
                    elif l2.strip().startswith("modality:"):
                        current["taxonomy"]["modality"] = strip_comment(l2.split(":",1)[1])
                    elif l2.strip() == "topic:":
                        i += 1
                        topics = []
                        while i < len(lines):
                            l3 = lines[i]
                            if l3.strip() == "":
                                i += 1
                                continue
                            if len(l3) - len(l3.lstrip(" ")) < 4:
                                break
                            l3s = l3.strip()
                            if l3s.startswith("-"):
                                topics.append(l3s[1:].strip())
                            i += 1
                        current["taxonomy"]["topic"] = topics
                        continue
                    i += 1
                continue

            if key == "evidence":
                i += 1
                ev = []
                while i < len(lines):
                    l2 = lines[i]
                    if l2.strip() == "":
                        i += 1
                        continue
                    if len(l2) - len(l2.lstrip(" ")) < 2:
                        break
                    if l2.strip().startswith("-"):
                        item = {"url": "", "title": "", "date": "", "notes": ""}
                        # line is: - url: ...
                        rest2 = l2.strip()[1:].strip()
                        if rest2.startswith("url:"):
                            item["url"] = rest2.split(":",1)[1].strip()
                        i += 1
                        while i < len(lines):
                            l3 = lines[i]
                            if l3.strip() == "":
                                i += 1
                                continue
                            if len(l3) - len(l3.lstrip(" ")) < 4:
                                break
                            l3s = l3.strip()
                            if l3s.startswith("title:"):
                                item["title"] = l3s.split(":",1)[1].strip()
                            elif l3s.startswith("date:"):
                                item["date"] = l3s.split(":",1)[1].strip()
                            elif l3s.startswith("notes:"):
                                # expects block scalar
                                if l3s.endswith("|"):
                                    val, i = parse_block(lines, i + 1, indent=6)
                                    item["notes"] = val
                                    continue
                                else:
                                    item["notes"] = l3s.split(":",1)[1].strip()
                            i += 1
                        ev.append({k:v for k,v in item.items() if v != ""})
                        continue
                    i += 1
                current["evidence"] = ev
                continue

            # regular flat keys
            current[key] = strip_comment(rest)
            i += 1
            continue

        i += 1

    if current and current.get("id"):
        claims.append(current)

    # small cleanup: ensure topics list exists
    for c in claims:
        t = c.get("taxonomy") or {}
        if not isinstance(t.get("topic"), list):
            t["topic"] = []
        c["taxonomy"] = t

    OUT.write_text(json.dumps(claims, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(claims)} claims -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
