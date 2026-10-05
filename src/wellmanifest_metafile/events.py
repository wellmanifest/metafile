"""Append-only JSONL event stream and state reduction for wellmanifest.metafile."""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from .core import Metafile


@dataclass
class MetafileEvent:
    event: str
    docId: str
    v: int = 1
    ts: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    actor: Optional[str] = None
    node: Optional[str] = None
    delta: Dict[str, Any] = field(default_factory=dict)
    snapshot: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}

    def to_jsonl(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MetafileEvent:
        return cls(
            event=data["event"],
            docId=data["docId"],
            v=data.get("v", 1),
            ts=data.get("ts") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            actor=data.get("actor"),
            node=data.get("node"),
            delta=data.get("delta") or {},
            snapshot=data.get("snapshot"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> MetafileEvent:
        return cls.from_dict(json.loads(json_str))


def fold_events(events: List[MetafileEvent], base: Optional[Metafile] = None) -> Optional[Metafile]:
    """Reduce a list of append-only events into the current Metafile state."""
    if not events:
        return base

    doc_id = events[0].docId
    accumulated: Dict[str, Any] = base.to_dict() if base else {"docId": doc_id, "schema": "wellmanifest.metafile/v1"}

    for ev in events:
        # If event contains full snapshot, start from it
        if ev.snapshot:
            accumulated.update(ev.snapshot)
        # Apply deltas
        if ev.delta:
            for k, v in ev.delta.items():
                if isinstance(v, dict) and isinstance(accumulated.get(k), dict):
                    accumulated[k].update(v)
                else:
                    accumulated[k] = v

        # Provenance tracking
        if "provenance" not in accumulated:
            accumulated["provenance"] = {}
        accumulated["provenance"]["lastEvent"] = ev.event
        accumulated["provenance"]["lastModifiedAt"] = ev.ts
        if ev.node:
            accumulated["provenance"]["lastNode"] = ev.node
        if ev.actor:
            accumulated["provenance"]["lastActor"] = ev.actor

    return Metafile.from_dict(accumulated)


def read_pdf_events(file_path: Path | str) -> List[MetafileEvent]:
    """Read all append-only event lines embedded in a PDF file."""
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return []

    raw = path.read_bytes()
    events: List[MetafileEvent] = []

    # Search for all /WellmanifestEvent (...) objects
    matches = re.finditer(rb"/WellmanifestEvent\s*\((.*?)\)", raw, re.DOTALL)
    for m in matches:
        val = m.group(1).decode("latin1", errors="ignore")
        val = val.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")
        try:
            events.append(MetafileEvent.from_json(val))
        except Exception:
            pass

    # Also search for embedded JSONL streams
    stream_matches = re.finditer(rb"% --- Wellmanifest JSONL Event ---\s*(\{.*?\})", raw)
    for sm in stream_matches:
        try:
            events.append(MetafileEvent.from_json(sm.group(1).decode("utf-8")))
        except Exception:
            pass

    return events


def append_pdf_event(file_path: Path | str, event: MetafileEvent) -> bool:
    """Append a discrete lifecycle event directly to a PDF file without rewriting existing content."""
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return False

    raw = path.read_bytes()
    if not raw.startswith(b"%PDF-"):
        return False

    def escape_pdf(text: str) -> str:
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    jsonl_line = event.to_jsonl()
    escaped_event = escape_pdf(jsonl_line)

    eof_pos = raw.rfind(b"%%EOF")
    if eof_pos == -1:
        eof_pos = len(raw)

    update = (
        b"\n% --- Wellmanifest JSONL Event ---\n"
        + jsonl_line.encode("utf-8") +
        b"\n9998 0 obj\n"
        b"<< /Type /WellmanifestEvent /WellmanifestEvent (" + escaped_event.encode("ascii", errors="ignore") + b") >>\n"
        b"endobj\n"
        b"startxref\n"
        + str(eof_pos).encode("ascii") +
        b"\n%%EOF\n"
    )

    path.write_bytes(raw[:eof_pos] + update)
    return True
