"""MIME type detection and adapter dispatcher."""
from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Optional

from .core import Metafile
from .adapters.pdf import read_pdf_metafile, write_pdf_metafile
from .adapters.png import read_png_metafile, write_png_metafile
from .adapters.jpeg import read_jpeg_metafile, write_jpeg_metafile
from .adapters.eml import read_eml_metafile, write_eml_metafile
from .adapters.text import read_text_metafile, write_text_metafile

SUPPORTED_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".eml": "message/rfc822",
    ".msg": "message/rfc822",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".txt": "text/plain",
}


def detect_mime(file_path: Path | str) -> str:
    """Detect MIME type by extension or file signature."""
    path = Path(file_path)
    ext = path.suffix.lower()
    if ext in SUPPORTED_EXTENSIONS:
        return SUPPORTED_EXTENSIONS[ext]
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def supports_mime(file_path: Path | str) -> bool:
    """Check if the given file has an available embedded metafile adapter."""
    ext = Path(file_path).suffix.lower()
    return ext in SUPPORTED_EXTENSIONS


def read_metafile(file_path: Path | str) -> Optional[Metafile]:
    """Read embedded wellmanifest metadata from any supported file."""
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return None

    mime = detect_mime(path)
    if mime == "application/pdf":
        return read_pdf_metafile(path)
    elif mime == "image/png":
        return read_png_metafile(path)
    elif mime == "image/jpeg":
        return read_jpeg_metafile(path)
    elif mime == "message/rfc822":
        return read_eml_metafile(path)
    elif mime in ("text/markdown", "text/plain"):
        return read_text_metafile(path)

    return None


def write_metafile(file_path: Path | str, meta: Metafile) -> bool:
    """Embed wellmanifest metadata into any supported file."""
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return False

    mime = detect_mime(path)
    if mime == "application/pdf":
        return write_pdf_metafile(path, meta)
    elif mime == "image/png":
        return write_png_metafile(path, meta)
    elif mime == "image/jpeg":
        return write_jpeg_metafile(path, meta)
    elif mime == "message/rfc822":
        return write_eml_metafile(path, meta)
    elif mime in ("text/markdown", "text/plain"):
        return write_text_metafile(path, meta)

    return False
