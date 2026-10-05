"""Adapters for archive and office formats: ZIP, DOCX, XLSX."""
from __future__ import annotations

import io
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

from ..core import Metafile

META_ENTRY_PATH = "META-INF/metafile.json"


def read_zip_metafile(file_path: Path | str) -> Optional[Metafile]:
    path = Path(file_path)
    if not path.is_file():
        return None
    try:
        with zipfile.ZipFile(path, "r") as zf:
            if META_ENTRY_PATH in zf.namelist():
                content = zf.read(META_ENTRY_PATH).decode("utf-8")
                return Metafile.from_json(content)
            # Fallback to comment
            if zf.comment:
                try:
                    c = zf.comment.decode("utf-8")
                    if "wellmanifest" in c:
                        return Metafile.from_json(c)
                except Exception:
                    pass
    except Exception:
        pass
    return None


def write_zip_metafile(file_path: Path | str, meta: Metafile) -> None:
    path = Path(file_path)
    json_bytes = meta.to_json().encode("utf-8")

    # If file doesn't exist or is empty, create a new zip
    if not path.is_file() or path.stat().st_size == 0:
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(META_ENTRY_PATH, json_bytes)
        return

    # Update or add META-INF/metafile.json safely via temp file
    with tempfile.NamedTemporaryFile("wb", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        with zipfile.ZipFile(path, "r") as src, zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as dst:
            for item in src.infolist():
                if item.filename != META_ENTRY_PATH:
                    dst.writestr(item, src.read(item.filename))
            dst.writestr(META_ENTRY_PATH, json_bytes)
        shutil.move(str(tmp_path), str(path))
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


# DOCX and XLSX are Open Packaging Conventions (ZIP) archives
read_docx_metafile = read_zip_metafile
write_docx_metafile = write_zip_metafile

read_xlsx_metafile = read_zip_metafile
write_xlsx_metafile = write_zip_metafile
