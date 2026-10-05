"""wellmanifest_metafile: Universal standard for embedded file metadata."""
from __future__ import annotations

from .core import Metafile
from .detector import read_metafile, write_metafile, supports_mime
from .events import MetafileEvent, read_pdf_events, append_pdf_event, fold_events

__all__ = [
    "Metafile",
    "MetafileEvent",
    "read_metafile",
    "write_metafile",
    "read_pdf_events",
    "append_pdf_event",
    "fold_events",
    "supports_mime",
]

__version__ = "0.1.0"
