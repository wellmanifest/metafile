"""PDF metadata adapter (ISO 32000-1 / PDF/A)."""
from __future__ import annotations

import io
import json
import re
from pathlib import Path
from typing import Optional

from ..core import Metafile


def read_pdf_metafile(file_path: Path | str) -> Optional[Metafile]:
    """Extract embedded wellmanifest metafile from a PDF file."""
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return None

    raw_bytes = path.read_bytes()

    meta = None

    # 1. Search for embedded JSON string marker (taking latest incremental update)
    # Format: /WellmanifestJSON (base64_or_json) or stream with marker
    matches = list(re.finditer(rb"/WellmanifestJSON\s*\((.*?)\)", raw_bytes, re.DOTALL))
    if matches:
        val = matches[-1].group(1).decode("latin1", errors="ignore")
        val = val.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")
        try:
            meta = Metafile.from_json(val)
        except Exception:
            pass

    # 2. Search for raw JSON payload within any metadata stream
    if meta is None:
        json_block = re.search(rb'\{\s*"schema":\s*"wellmanifest\.metafile/v1".*?\}', raw_bytes, re.DOTALL)
        if json_block:
            try:
                meta = Metafile.from_json(json_block.group(0).decode("utf-8"))
            except Exception:
                pass

    # 3. Extract standard Info dictionary fields
    if meta is None:
        doc_id_m = re.search(rb"/DocId\s*\((.*?)\)", raw_bytes)
        contractor_m = re.search(rb"/Contractor\s*\((.*?)\)", raw_bytes)
        amount_m = re.search(rb"/Amount\s*\((.*?)\)", raw_bytes)
        currency_m = re.search(rb"/Currency\s*\((.*?)\)", raw_bytes)
        date_m = re.search(rb"/Date\s*\((.*?)\)", raw_bytes)
        type_m = re.search(rb"/Type\s*\((.*?)\)", raw_bytes)
        country_m = re.search(rb"/Country\s*\((.*?)\)", raw_bytes)
        city_m = re.search(rb"/City\s*\((.*?)\)", raw_bytes)
        address_m = re.search(rb"/Address\s*\((.*?)\)", raw_bytes)
        node_m = re.search(rb"/Node\s*\((.*?)\)", raw_bytes)

        if doc_id_m:
            data = {
                "docId": doc_id_m.group(1).decode("latin1", errors="ignore"),
                "contractor": contractor_m.group(1).decode("latin1", errors="ignore") if contractor_m else None,
                "amount": amount_m.group(1).decode("latin1", errors="ignore") if amount_m else None,
                "currency": currency_m.group(1).decode("latin1", errors="ignore") if currency_m else "PLN",
                "date": date_m.group(1).decode("latin1", errors="ignore") if date_m else None,
                "type": type_m.group(1).decode("latin1", errors="ignore") if type_m else None,
                "location": {
                    "country": country_m.group(1).decode("latin1", errors="ignore") if country_m else None,
                    "city": city_m.group(1).decode("latin1", errors="ignore") if city_m else None,
                    "address": address_m.group(1).decode("latin1", errors="ignore") if address_m else None,
                    "node": node_m.group(1).decode("latin1", errors="ignore") if node_m else None,
                }
            }
            meta = Metafile.from_dict(data)

    if meta is not None:
        try:
            from ..events import read_pdf_events, fold_events
            events = read_pdf_events(path)
            if events:
                meta = fold_events(events, base=meta)
        except Exception:
            pass
        return meta

    return None


def write_pdf_metafile(file_path: Path | str, meta: Metafile) -> bool:
    """Embed wellmanifest metafile into a PDF file using an incremental update.

    Non-destructively appends an Info dictionary update and metafile stream before EOF.
    """
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return False

    raw = path.read_bytes()
    if not raw.startswith(b"%PDF-"):
        return False

    def escape_pdf(text: str) -> str:
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    json_payload = meta.to_json(indent=0).replace("\n", " ")
    escaped_json = escape_pdf(json_payload)

    # Prepare info dictionary extension
    fields = [
        f"/WellmanifestDocId ({escape_pdf(meta.docId)})",
        f"/DocId ({escape_pdf(meta.docId)})",
        f"/WellmanifestJSON ({escaped_json})",
    ]
    if meta.title:
        fields.append(f"/Title ({escape_pdf(meta.title)})")
    if meta.type:
        fields.append(f"/Subject ({escape_pdf(meta.type)})")
    if meta.accounting.contractor:
        fields.append(f"/Contractor ({escape_pdf(meta.accounting.contractor)})")
    if meta.accounting.amount:
        fields.append(f"/Amount ({escape_pdf(str(meta.accounting.amount))})")
    if meta.currency:
        fields.append(f"/Currency ({escape_pdf(meta.currency)})")
    if meta.location.country:
        fields.append(f"/Country ({escape_pdf(meta.location.country)})")
    if meta.location.city:
        fields.append(f"/City ({escape_pdf(meta.location.city)})")
    if meta.location.address:
        fields.append(f"/Address ({escape_pdf(meta.location.address)})")
    if meta.location.node:
        fields.append(f"/Node ({escape_pdf(meta.location.node)})")
    if meta.date:
        fields.append(f"/Date ({escape_pdf(meta.date)})")

    info_dict = f"<< {' '.join(fields)} >>".encode("ascii", errors="ignore")

    # Incremental update: append new object containing the metadata
    # Find last xref offset
    eof_pos = raw.rfind(b"%%EOF")
    if eof_pos == -1:
        eof_pos = len(raw)

    update = (
        b"\n% --- Wellmanifest Metafile v1 ---\n"
        b"9999 0 obj\n"
        + info_dict +
        b"\nendobj\n"
        b"trailer\n"
        b"<< /Info 9999 0 R >>\n"
        b"startxref\n"
        + str(eof_pos).encode("ascii") +
        b"\n%%EOF\n"
    )

    path.write_bytes(raw[:eof_pos] + update)
    return True
