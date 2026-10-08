"""Schema validation and conformance verification for wellmanifest.metafile."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import jsonschema
from jsonschema import Draft7Validator

from .core import Metafile
from .events import MetafileEvent, read_events
from .detector import read_metafile, detect_mime, supports_mime

_SCHEMAS_DIR = Path(__file__).parent / "schemas"
if not _SCHEMAS_DIR.is_dir():
    # Fallback to repo root schemas
    _SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"

_V1_SCHEMA_PATH = _SCHEMAS_DIR / "metafile.v1.schema.json"
_EVENT_SCHEMA_PATH = _SCHEMAS_DIR / "metafile.event.schema.json"

_CACHED_V1_SCHEMA: Optional[Dict[str, Any]] = None
_CACHED_EVENT_SCHEMA: Optional[Dict[str, Any]] = None


def get_metafile_schema() -> Dict[str, Any]:
    """Retrieve and cache the canonical metafile.v1 JSON schema."""
    global _CACHED_V1_SCHEMA
    if _CACHED_V1_SCHEMA is None:
        if not _V1_SCHEMA_PATH.is_file():
            raise FileNotFoundError(f"Metafile v1 schema not found at {_V1_SCHEMA_PATH}")
        _CACHED_V1_SCHEMA = json.loads(_V1_SCHEMA_PATH.read_text(encoding="utf-8"))
    return _CACHED_V1_SCHEMA


def get_event_schema() -> Dict[str, Any]:
    """Retrieve and cache the canonical metafile.event JSON schema."""
    global _CACHED_EVENT_SCHEMA
    if _CACHED_EVENT_SCHEMA is None:
        if not _EVENT_SCHEMA_PATH.is_file():
            raise FileNotFoundError(f"Metafile event schema not found at {_EVENT_SCHEMA_PATH}")
        _CACHED_EVENT_SCHEMA = json.loads(_EVENT_SCHEMA_PATH.read_text(encoding="utf-8"))
    return _CACHED_EVENT_SCHEMA


def validate_metafile(target: Union[Metafile, Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """Validate a Metafile instance or dictionary against schemas/metafile.v1.schema.json."""
    if isinstance(target, Metafile):
        payload = target.to_dict()
    elif isinstance(target, dict):
        payload = target
    else:
        return False, [f"Expected Metafile or dict, got {type(target).__name__}"]

    schema = get_metafile_schema()
    validator = Draft7Validator(schema)
    errors: List[str] = []
    for err in sorted(validator.iter_errors(payload), key=lambda e: e.path):
        loc = ".".join(str(p) for p in err.path) if err.path else "root"
        errors.append(f"[{loc}] {err.message}")

    return len(errors) == 0, errors


def validate_event(target: Union[MetafileEvent, Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """Validate a MetafileEvent instance or dictionary against schemas/metafile.event.schema.json."""
    if isinstance(target, MetafileEvent):
        payload = target.to_dict()
    elif isinstance(target, dict):
        payload = target
    else:
        return False, [f"Expected MetafileEvent or dict, got {type(target).__name__}"]

    schema = get_event_schema()
    validator = Draft7Validator(schema)
    errors: List[str] = []
    for err in sorted(validator.iter_errors(payload), key=lambda e: e.path):
        loc = ".".join(str(p) for p in err.path) if err.path else "root"
        errors.append(f"[{loc}] {err.message}")

    return len(errors) == 0, errors


def validate_file(file_path: Union[Path, str], check_hash: bool = False) -> Dict[str, Any]:
    """Inspect and comprehensively validate a file's embedded metadata and event log.

    Returns a report dictionary with validation state, schema errors, and diagnostics.
    """
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return {
            "valid": False,
            "file": str(path),
            "errors": [f"File not found: {path}"],
            "warnings": [],
            "hasMetadata": False,
            "eventsCount": 0,
        }

    mime = detect_mime(path)
    supported = supports_mime(path)
    errors: List[str] = []
    warnings: List[str] = []

    meta = read_metafile(path)
    has_meta = meta is not None
    doc_id = meta.docId if meta else None

    if not has_meta:
        errors.append(f"No embedded wellmanifest metadata found in file ({mime})")
    else:
        # Validate Metafile schema
        is_meta_valid, meta_errors = validate_metafile(meta)
        if not is_meta_valid:
            errors.extend(meta_errors)

    # Read and validate embedded events
    events = read_events(path)
    for idx, ev in enumerate(events, 1):
        is_ev_valid, ev_errors = validate_event(ev)
        if not is_ev_valid:
            for err in ev_errors:
                errors.append(f"Event #{idx} ({ev.event}): {err}")

    # Optional SHA256 integrity check
    if check_hash and meta and meta.hashes.sha256:
        raw_bytes = path.read_bytes()
        actual_sha = hashlib.sha256(raw_bytes).hexdigest()
        if actual_sha.lower() != meta.hashes.sha256.lower():
            warnings.append(
                f"SHA256 mismatch: embedded '{meta.hashes.sha256}' vs current file content '{actual_sha}' "
                "(note: metadata embedding alters byte-level file hash unless pre-computed)"
            )

    return {
        "valid": len(errors) == 0,
        "file": str(path),
        "mime": mime,
        "supported": supported,
        "hasMetadata": has_meta,
        "docId": doc_id,
        "eventsCount": len(events),
        "errors": errors,
        "warnings": warnings,
    }
