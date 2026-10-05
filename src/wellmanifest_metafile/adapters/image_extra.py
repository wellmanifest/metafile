"""Extended image adapters for WebP, GIF, TIFF, BMP, ICO, AVIF."""
from __future__ import annotations

import io
import json
import re
from pathlib import Path
from typing import Optional

from PIL import Image, ExifTags

from ..core import Metafile

TRAILER_PREFIX = b"\n# wellmanifest-metafile:"


# ---------------- GIF ----------------
def read_gif_metafile(file_path: Path | str) -> Optional[Metafile]:
    path = Path(file_path)
    try:
        with Image.open(path) as img:
            comment = img.info.get("comment")
            if comment:
                if isinstance(comment, bytes):
                    comment = comment.decode("utf-8", errors="replace")
                return Metafile.from_json(comment)
    except Exception:
        pass
    # Fallback to trailer check
    return _read_trailer_metafile(path)


def write_gif_metafile(file_path: Path | str, meta: Metafile) -> None:
    path = Path(file_path)
    try:
        with Image.open(path) as img:
            frames = []
            try:
                while True:
                    frames.append(img.copy())
                    img.seek(img.tell() + 1)
            except EOFError:
                pass
            first = frames[0] if frames else img
            comment_bytes = meta.to_json().encode("utf-8")
            if len(frames) > 1:
                first.save(path, save_all=True, append_images=frames[1:], comment=comment_bytes)
            else:
                first.save(path, comment=comment_bytes)
            return
    except Exception:
        pass
    _write_trailer_metafile(path, meta)


# ---------------- TIFF ----------------
def read_tiff_metafile(file_path: Path | str) -> Optional[Metafile]:
    path = Path(file_path)
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            if exif:
                # 37510 is UserComment, 270 is ImageDescription
                for tag_id in (37510, 270):
                    val = exif.get(tag_id)
                    if val:
                        if isinstance(val, bytes):
                            val = val.decode("utf-8", errors="replace")
                        if "wellmanifest" in val or "docId" in val:
                            return Metafile.from_json(val)
    except Exception:
        pass
    return _read_trailer_metafile(path)


def write_tiff_metafile(file_path: Path | str, meta: Metafile) -> None:
    path = Path(file_path)
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            exif[270] = meta.to_json()  # ImageDescription
            exif[37510] = meta.to_json()  # UserComment
            img.save(path, exif=exif)
            return
    except Exception:
        pass
    _write_trailer_metafile(path, meta)


# ---------------- WebP ----------------
def read_webp_metafile(file_path: Path | str) -> Optional[Metafile]:
    path = Path(file_path)
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            if exif:
                for tag_id in (37510, 270):
                    val = exif.get(tag_id)
                    if val:
                        if isinstance(val, bytes):
                            val = val.decode("utf-8", errors="replace")
                        if "wellmanifest" in val or "docId" in val:
                            return Metafile.from_json(val)
    except Exception:
        pass
    return _read_trailer_metafile(path)


def write_webp_metafile(file_path: Path | str, meta: Metafile) -> None:
    path = Path(file_path)
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            exif[270] = meta.to_json()
            exif[37510] = meta.to_json()
            img.save(path, "WEBP", exif=exif)
            return
    except Exception:
        pass
    _write_trailer_metafile(path, meta)


# ---------------- BMP, ICO, AVIF Trailer Fallback ----------------
def _read_trailer_metafile(file_path: Path | str) -> Optional[Metafile]:
    path = Path(file_path)
    try:
        data = path.read_bytes()
        idx = data.rfind(TRAILER_PREFIX)
        if idx != -1:
            raw = data[idx + len(TRAILER_PREFIX):].strip().decode("utf-8")
            return Metafile.from_json(raw)
    except Exception:
        pass
    return None


def _write_trailer_metafile(file_path: Path | str, meta: Metafile) -> None:
    path = Path(file_path)
    data = path.read_bytes() if path.is_file() else b""
    idx = data.rfind(TRAILER_PREFIX)
    if idx != -1:
        data = data[:idx]
    trailer = TRAILER_PREFIX + meta.to_json().encode("utf-8") + b"\n"
    path.write_bytes(data + trailer)


read_bmp_metafile = _read_trailer_metafile
write_bmp_metafile = _write_trailer_metafile

read_ico_metafile = _read_trailer_metafile
write_ico_metafile = _write_trailer_metafile

read_avif_metafile = _read_trailer_metafile
write_avif_metafile = _write_trailer_metafile
