"""Core data structures and serialization for wellmanifest.metafile/v1."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional


@dataclass
class AccountingMeta:
    amount: Optional[str] = None
    currency: str = "PLN"
    contractor: Optional[str] = None
    contractorNip: Optional[str] = None
    buyer: Optional[str] = None
    buyerNip: Optional[str] = None
    iban: Optional[str] = None
    period: Optional[str] = None
    category: Optional[str] = "koszty"
    subfolder: Optional[str] = "koszty"
    invoiceNumber: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HashesMeta:
    sha256: Optional[str] = None
    textSha256: Optional[str] = None
    dhash: Optional[str] = None
    phash: Optional[str] = None


@dataclass
class OcrMeta:
    backend: Optional[str] = None
    chars: int = 0
    confidence: Optional[float] = None
    text: str = ""


@dataclass
class ProvenanceMeta:
    createdAt: Optional[str] = None
    stagedAt: Optional[str] = None
    routedAt: Optional[str] = None
    deviceId: Optional[str] = None
    seriesId: Optional[str] = None
    host: Optional[str] = None
    sourcePath: Optional[str] = None
    originalFilename: Optional[str] = None


@dataclass
class Metafile:
    docId: str
    schema: str = "wellmanifest.metafile/v1"
    urn: Optional[str] = None
    type: Optional[str] = None
    date: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    accounting: AccountingMeta = field(default_factory=AccountingMeta)
    hashes: HashesMeta = field(default_factory=HashesMeta)
    ocr: OcrMeta = field(default_factory=OcrMeta)
    provenance: ProvenanceMeta = field(default_factory=ProvenanceMeta)
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metafile to clean JSON-serializable dictionary."""
        def clean(val: Any) -> Any:
            if isinstance(val, dict):
                return {k: clean(v) for k, v in val.items() if v is not None}
            elif isinstance(val, list):
                return [clean(v) for v in val]
            return val

        raw = asdict(self)
        cleaned = clean(raw)
        cleaned["schema"] = "wellmanifest.metafile/v1"
        return cleaned

    def to_json(self, indent: int = 2) -> str:
        """Serialize metafile to formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Metafile:
        """Instantiate Metafile from raw dictionary."""
        if not isinstance(data, dict):
            raise ValueError("Metafile data must be a dictionary")

        doc_id = data.get("docId") or data.get("id") or "UNKNOWN-DOC"
        
        acc_raw = data.get("accounting") or {}
        hashes_raw = data.get("hashes") or {}
        ocr_raw = data.get("ocr") or {}
        prov_raw = data.get("provenance") or {}

        # If flat dictionary was passed (backwards compatibility with urirun / faktury json)
        if not acc_raw:
            if any(k in data for k in ("amount", "contractor", "currency", "nip")):
                acc_raw = {
                    "amount": str(data["amount"]) if data.get("amount") is not None else None,
                    "currency": data.get("currency", "PLN"),
                    "contractor": data.get("contractor"),
                    "contractorNip": data.get("nip") or data.get("contractorNip"),
                    "category": data.get("category", "koszty"),
                    "subfolder": data.get("subfolder", "koszty"),
                }

        if not hashes_raw:
            hashes_raw = {
                "sha256": data.get("sourceSha256") or data.get("sha256"),
                "textSha256": data.get("textSha256"),
                "dhash": data.get("dhash"),
                "phash": data.get("phash"),
            }

        if not ocr_raw and (data.get("text") or data.get("ocrText")):
            ocr_raw = {
                "backend": data.get("ocrBackend", "paddle"),
                "chars": int(data.get("ocrChars") or len(data.get("text") or "")),
                "text": str(data.get("text") or data.get("ocrText") or ""),
            }

        return cls(
            docId=str(doc_id),
            schema=str(data.get("schema", "wellmanifest.metafile/v1")),
            urn=data.get("urn") or data.get("uri"),
            type=data.get("type"),
            date=data.get("date"),
            title=data.get("title"),
            description=data.get("description"),
            accounting=AccountingMeta(
                amount=acc_raw.get("amount"),
                currency=acc_raw.get("currency", "PLN"),
                contractor=acc_raw.get("contractor"),
                contractorNip=acc_raw.get("contractorNip"),
                buyer=acc_raw.get("buyer"),
                buyerNip=acc_raw.get("buyerNip"),
                iban=acc_raw.get("iban"),
                period=acc_raw.get("period"),
                category=acc_raw.get("category", "koszty"),
                subfolder=acc_raw.get("subfolder", "koszty"),
                invoiceNumber=acc_raw.get("invoiceNumber"),
                extra=acc_raw.get("extra", {}),
            ),
            hashes=HashesMeta(
                sha256=hashes_raw.get("sha256"),
                textSha256=hashes_raw.get("textSha256"),
                dhash=hashes_raw.get("dhash"),
                phash=hashes_raw.get("phash"),
            ),
            ocr=OcrMeta(
                backend=ocr_raw.get("backend"),
                chars=int(ocr_raw.get("chars", 0)),
                confidence=ocr_raw.get("confidence"),
                text=ocr_raw.get("text", ""),
            ),
            provenance=ProvenanceMeta(
                createdAt=prov_raw.get("createdAt") or data.get("createdAt"),
                stagedAt=prov_raw.get("stagedAt"),
                routedAt=prov_raw.get("routedAt"),
                deviceId=prov_raw.get("deviceId") or data.get("deviceId"),
                seriesId=prov_raw.get("seriesId") or data.get("series_id"),
                host=prov_raw.get("host"),
                sourcePath=prov_raw.get("sourcePath") or data.get("originalPath"),
                originalFilename=prov_raw.get("originalFilename") or data.get("fileName"),
            ),
            extra=data.get("extra", {}),
        )

    @classmethod
    def from_json(cls, json_str: str) -> Metafile:
        """Parse Metafile from JSON string."""
        return cls.from_dict(json.loads(json_str))
