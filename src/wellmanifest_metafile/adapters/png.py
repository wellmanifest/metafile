"""PNG metadata adapter (ISO/IEC 15948)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from PIL import Image, PngImagePlugin

from ..core import Metafile

CHUNK_KEYWORD = "wellmanifest:metafile"


def read_png_metafile(file_path: Path | str) -> Optional[Metafile]:
    """Extract embedded wellmanifest metafile from a PNG file."""
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return None

    try:
        with Image.open(path) as img:
            if img.format != "PNG":
                return None
            info = img.text or {}
            raw_json = info.get(CHUNK_KEYWORD) or info.get("Wellmanifest") or info.get("wellmanifest")
            if raw_json:
                return Metafile.from_json(raw_json)
    except Exception:
        pass
    return None


def write_png_metafile(file_path: Path | str, meta: Metafile) -> bool:
    """Embed wellmanifest metafile into a PNG file without recompressing pixel data."""
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return False

    try:
        with Image.open(path) as img:
            if img.format != "PNG":
                return False
            png_info = PngImagePlugin.PngInfo()
            # Copy existing metadata
            for k, v in (img.text or {}).items():
                if k != CHUNK_KEYWORD:
                    png_info.add_text(k, str(v))
            # Inject canonical wellmanifest JSON
            png_info.add_text(CHUNK_KEYWORD, meta.to_json(indent=0))
            img.save(path, format="PNG", pnginfo=png_info)
            return True
    except Exception:
        return False
