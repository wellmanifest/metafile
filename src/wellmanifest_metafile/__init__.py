"""wellmanifest_metafile: Universal standard for embedded file metadata."""
from __future__ import annotations

from .core import Metafile
from .detector import read_metafile, write_metafile, supports_mime

__all__ = [
    "Metafile",
    "read_metafile",
    "write_metafile",
    "supports_mime",
]

__version__ = "0.1.0"
