"""Markdown and Plain Text metadata adapter (YAML Frontmatter)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import yaml

from ..core import Metafile


def read_text_metafile(file_path: Path | str) -> Optional[Metafile]:
    """Extract embedded wellmanifest metafile from Markdown or text frontmatter."""
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return None

    try:
        content = path.read_text(encoding="utf-8")
        # 1. Match standard YAML frontmatter: ^---\n(.*?)\n---\n
        fm_match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", content, re.DOTALL)
        if fm_match:
            parsed = yaml.safe_load(fm_match.group(1))
            if isinstance(parsed, dict):
                wm_dict = parsed.get("wellmanifest") or parsed.get("metafile") or parsed
                if isinstance(wm_dict, dict) and (wm_dict.get("schema") == "wellmanifest.metafile/v1" or wm_dict.get("docId")):
                    return Metafile.from_dict(wm_dict)

        # 2. Match HTML comment: <!-- wellmanifest:metafile:v1 { ... } -->
        comment_match = re.search(r"<!--\s*wellmanifest:metafile:v1\s*(\{.*?\})\s*-->", content, re.DOTALL)
        if comment_match:
            return Metafile.from_json(comment_match.group(1))
    except Exception:
        pass
    return None


def write_text_metafile(file_path: Path | str, meta: Metafile) -> bool:
    """Embed wellmanifest metafile into Markdown or text as YAML frontmatter."""
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return False

    try:
        content = path.read_text(encoding="utf-8")
        payload = meta.to_dict()

        # Remove existing frontmatter if present
        fm_match = re.match(r"^---\r?\n.*?\r?\n---\r?\n", content, re.DOTALL)
        if fm_match:
            body = content[fm_match.end():]
        else:
            body = content

        fm_yaml = yaml.dump({"wellmanifest": payload}, sort_keys=False, allow_unicode=True)
        new_content = f"---\n{fm_yaml}---\n{body}"
        path.write_text(new_content, encoding="utf-8")
        return True
    except Exception:
        return False
