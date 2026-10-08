"""wellmanifest_metafile: Universal standard for embedded file metadata."""
from __future__ import annotations

from .core import (
    Metafile,
    AccountingMeta,
    LocationMeta,
    HashesMeta,
    OcrMeta,
    ProvenanceMeta,
)
from .detector import read_metafile, write_metafile, supports_mime, detect_mime
from .events import (
    MetafileEvent,
    read_events,
    append_event,
    read_pdf_events,
    append_pdf_event,
    fold_events,
)
from .validator import (
    validate_metafile,
    validate_event,
    validate_file,
    get_metafile_schema,
    get_event_schema,
)

__all__ = [
    "Metafile",
    "AccountingMeta",
    "LocationMeta",
    "HashesMeta",
    "OcrMeta",
    "ProvenanceMeta",
    "MetafileEvent",
    "read_metafile",
    "write_metafile",
    "read_events",
    "append_event",
    "read_pdf_events",
    "append_pdf_event",
    "fold_events",
    "supports_mime",
    "detect_mime",
    "validate_metafile",
    "validate_event",
    "validate_file",
    "get_metafile_schema",
    "get_event_schema",
]

__version__ = "0.1.0"

