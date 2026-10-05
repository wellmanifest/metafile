"""JPEG metadata adapter (EXIF / XMP)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from PIL import Image

from ..core import Metafile

USER_COMMENT_TAG = 0x9286  # EXIF UserComment tag


def read_jpeg_metafile(file_path: Path | str) -> Optional[Metafile]:
    """Extract embedded wellmanifest metafile from a JPEG file."""
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return None

    try:
        with Image.open(path) as img:
            if img.format != "JPEG":
                return None
            exif = img.getexif()
            if exif and USER_COMMENT_TAG in exif:
                val = exif[USER_COMMENT_TAG]
                if isinstance(val, bytes):
                    # Check for UNICODE\0 prefix
                    if val.startswith(b"UNICODE\x00"):
                        val = val[8:].decode("utf-16", errors="ignore")
                    else:
                        val = val.decode("utf-8", errors="ignore")
                if isinstance(val, str) and "wellmanifest.metafile/v1" in val:
                    return Metafile.from_json(val)
    except Exception:
        pass
    return None


def write_jpeg_metafile(file_path: Path | str, meta: Metafile) -> bool:
    """Embed wellmanifest metafile into a JPEG file using EXIF UserComment."""
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return False

    try:
        with Image.open(path) as img:
            if img.format != "JPEG":
                return False
            exif = img.getexif()
            payload = meta.to_json(indent=0)
            exif[USER_COMMENT_TAG] = payload
            img.save(path, format="JPEG", exif=exif, quality=95)
            return True
    except Exception:
        return False
