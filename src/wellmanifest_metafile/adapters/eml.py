"""EML (RFC 5322 / MIME) metadata adapter."""
from __future__ import annotations

import base64
import email
import json
from pathlib import Path
from typing import Optional

from ..core import Metafile


def read_eml_metafile(file_path: Path | str) -> Optional[Metafile]:
    """Extract embedded wellmanifest metafile from an EML file."""
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return None

    try:
        raw_text = path.read_text(encoding="utf-8", errors="replace")
        msg = email.message_from_string(raw_text)

        # 1. Base64 payload header
        b64_header = msg.get("X-Wellmanifest-Payload-B64")
        if b64_header:
            try:
                decoded = base64.b64decode(b64_header).decode("utf-8")
                return Metafile.from_json(decoded)
            except Exception:
                pass

        # 2. Raw JSON header
        json_header = msg.get("X-Wellmanifest-JSON")
        if json_header:
            try:
                return Metafile.from_json(json_header)
            except Exception:
                pass

        # 3. Individual standard headers
        doc_id = msg.get("X-Wellmanifest-DocID") or msg.get("X-Document-ID")
        if doc_id:
            data = {
                "docId": doc_id,
                "type": msg.get("X-Wellmanifest-Type") or msg.get("X-Document-Type"),
                "date": msg.get("X-Wellmanifest-Date") or msg.get("X-Document-Date"),
                "contractor": msg.get("X-Wellmanifest-Contractor") or msg.get("X-Document-Contractor"),
                "amount": msg.get("X-Wellmanifest-Amount") or msg.get("X-Document-Amount"),
                "currency": msg.get("X-Wellmanifest-Currency") or msg.get("X-Document-Currency") or "PLN",
                "location": {
                    "country": msg.get("X-Wellmanifest-Country"),
                    "city": msg.get("X-Wellmanifest-City"),
                    "address": msg.get("X-Wellmanifest-Address"),
                    "node": msg.get("X-Wellmanifest-Node"),
                }
            }
            return Metafile.from_dict(data)
    except Exception:
        pass
    return None


def write_eml_metafile(file_path: Path | str, meta: Metafile) -> bool:
    """Embed wellmanifest metafile into an EML file headers."""
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return False

    try:
        raw_text = path.read_text(encoding="utf-8", errors="replace")
        msg = email.message_from_string(raw_text)

        # Remove existing headers if any
        headers_to_remove = [
            "X-Wellmanifest-DocID", "X-Wellmanifest-Type", "X-Wellmanifest-Date",
            "X-Wellmanifest-Contractor", "X-Wellmanifest-Amount", "X-Wellmanifest-Currency",
            "X-Wellmanifest-Country", "X-Wellmanifest-City", "X-Wellmanifest-Address", "X-Wellmanifest-Node",
            "X-Wellmanifest-Payload-B64"
        ]
        for h in headers_to_remove:
            while h in msg:
                del msg[h]

        # Add new headers
        msg["X-Wellmanifest-DocID"] = meta.docId
        if meta.type:
            msg["X-Wellmanifest-Type"] = meta.type
        if meta.date:
            msg["X-Wellmanifest-Date"] = meta.date
        if meta.accounting.contractor:
            msg["X-Wellmanifest-Contractor"] = meta.accounting.contractor
        if meta.accounting.amount:
            msg["X-Wellmanifest-Amount"] = str(meta.accounting.amount)
        if meta.currency:
            msg["X-Wellmanifest-Currency"] = meta.currency
        if meta.location.country:
            msg["X-Wellmanifest-Country"] = meta.location.country
        if meta.location.city:
            msg["X-Wellmanifest-City"] = meta.location.city
        if meta.location.address:
            msg["X-Wellmanifest-Address"] = meta.location.address
        if meta.location.node:
            msg["X-Wellmanifest-Node"] = meta.location.node

        b64_json = base64.b64encode(meta.to_json(indent=0).encode("utf-8")).decode("ascii")
        msg["X-Wellmanifest-Payload-B64"] = b64_json

        path.write_text(msg.as_string(), encoding="utf-8")
        return True
    except Exception:
        return False
