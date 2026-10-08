"""MIME type detection and adapter dispatcher across 30+ popular file formats."""
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
from .adapters.data import (
    read_json_metafile, write_json_metafile,
    read_jsonl_metafile, write_jsonl_metafile,
    read_xml_metafile, write_xml_metafile,
    read_csv_metafile, write_csv_metafile,
    read_yaml_metafile, write_yaml_metafile,
    read_html_metafile, write_html_metafile,
)
from .adapters.archive import (
    read_zip_metafile, write_zip_metafile,
    read_docx_metafile, write_docx_metafile,
    read_xlsx_metafile, write_xlsx_metafile,
)
from .adapters.image_extra import (
    read_webp_metafile, write_webp_metafile,
    read_gif_metafile, write_gif_metafile,
    read_tiff_metafile, write_tiff_metafile,
    read_bmp_metafile, write_bmp_metafile,
    read_ico_metafile, write_ico_metafile,
    read_avif_metafile, write_avif_metafile,
)
from .adapters.multimedia import (
    read_mp3_metafile, write_mp3_metafile,
    read_flac_metafile, write_flac_metafile,
    read_ogg_metafile, write_ogg_metafile,
    read_wav_metafile, write_wav_metafile,
    read_mp4_metafile, write_mp4_metafile,
    read_mkv_metafile, write_mkv_metafile,
    read_webm_metafile, write_webm_metafile,
)

# Registry of 30 standard format extensions and their read/write handlers
ADAPTER_MAP = {
    # 1. Documents & EML
    ".pdf": (read_pdf_metafile, write_pdf_metafile, "application/pdf"),
    ".eml": (read_eml_metafile, write_eml_metafile, "message/rfc822"),
    ".msg": (read_eml_metafile, write_eml_metafile, "message/rfc822"),

    # 2. Structured Data & Text
    ".json": (read_json_metafile, write_json_metafile, "application/json"),
    ".jsonl": (read_jsonl_metafile, write_jsonl_metafile, "application/x-ndjson"),
    ".xml": (read_xml_metafile, write_xml_metafile, "application/xml"),
    ".csv": (read_csv_metafile, write_csv_metafile, "text/csv"),
    ".tsv": (read_csv_metafile, write_csv_metafile, "text/tab-separated-values"),
    ".yaml": (read_yaml_metafile, write_yaml_metafile, "application/yaml"),
    ".yml": (read_yaml_metafile, write_yaml_metafile, "application/yaml"),
    ".md": (read_text_metafile, write_text_metafile, "text/markdown"),
    ".markdown": (read_text_metafile, write_text_metafile, "text/markdown"),
    ".txt": (read_text_metafile, write_text_metafile, "text/plain"),
    ".html": (read_html_metafile, write_html_metafile, "text/html"),
    ".htm": (read_html_metafile, write_html_metafile, "text/html"),

    # 3. Archives & Office
    ".zip": (read_zip_metafile, write_zip_metafile, "application/zip"),
    ".docx": (read_docx_metafile, write_docx_metafile, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ".xlsx": (read_xlsx_metafile, write_xlsx_metafile, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),

    # 4. Images / Graphics
    ".png": (read_png_metafile, write_png_metafile, "image/png"),
    ".jpg": (read_jpeg_metafile, write_jpeg_metafile, "image/jpeg"),
    ".jpeg": (read_jpeg_metafile, write_jpeg_metafile, "image/jpeg"),
    ".webp": (read_webp_metafile, write_webp_metafile, "image/webp"),
    ".svg": (read_xml_metafile, write_xml_metafile, "image/svg+xml"),
    ".gif": (read_gif_metafile, write_gif_metafile, "image/gif"),
    ".tiff": (read_tiff_metafile, write_tiff_metafile, "image/tiff"),
    ".tif": (read_tiff_metafile, write_tiff_metafile, "image/tiff"),
    ".bmp": (read_bmp_metafile, write_bmp_metafile, "image/bmp"),
    ".ico": (read_ico_metafile, write_ico_metafile, "image/x-icon"),
    ".avif": (read_avif_metafile, write_avif_metafile, "image/avif"),

    # 5. Audio
    ".mp3": (read_mp3_metafile, write_mp3_metafile, "audio/mpeg"),
    ".flac": (read_flac_metafile, write_flac_metafile, "audio/flac"),
    ".ogg": (read_ogg_metafile, write_ogg_metafile, "audio/ogg"),
    ".wav": (read_wav_metafile, write_wav_metafile, "audio/wav"),

    # 6. Video
    ".mp4": (read_mp4_metafile, write_mp4_metafile, "video/mp4"),
    ".m4a": (read_mp4_metafile, write_mp4_metafile, "audio/mp4"),
    ".mkv": (read_mkv_metafile, write_mkv_metafile, "video/x-matroska"),
    ".webm": (read_webm_metafile, write_webm_metafile, "video/webm"),
}


def detect_mime(file_path: Path | str) -> str:
    """Detect MIME type by extension or fallback to mimetypes."""
    path = Path(file_path)
    ext = path.suffix.lower()
    if ext in ADAPTER_MAP:
        return ADAPTER_MAP[ext][2]
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def supports_mime(file_path: Path | str) -> bool:
    """Check if the given file has an available embedded metafile adapter."""
    ext = Path(file_path).suffix.lower()
    return ext in ADAPTER_MAP


def read_metafile(file_path: Path | str) -> Optional[Metafile]:
    """Read embedded wellmanifest metadata from any supported file."""
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return None

    ext = path.suffix.lower()
    if ext in ADAPTER_MAP:
        reader = ADAPTER_MAP[ext][0]
        meta = reader(path)
        if meta is not None and ext != ".pdf":
            try:
                from .events import read_events, fold_events
                events = read_events(path)
                if events:
                    meta = fold_events(events, base=meta)
            except Exception:
                pass
        return meta

    return None


def write_metafile(file_path: Path | str, meta: Metafile) -> bool:
    """Write embedded wellmanifest metadata into any supported file."""
    path = Path(file_path).expanduser().resolve()
    ext = path.suffix.lower()
    if ext in ADAPTER_MAP:
        writer = ADAPTER_MAP[ext][1]
        res = writer(path, meta)
        return True if res is None or res is True else bool(res)

    return False
