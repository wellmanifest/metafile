"""CLI interface for wellmanifest-metafile."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from .core import Metafile
from .detector import read_metafile, write_metafile, supports_mime, detect_mime
from .events import MetafileEvent, read_events, append_event
from .validator import validate_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="metafile",
        description="Wellmanifest Metafile: Read and embed self-contained metadata across MIME types.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Command: read
    p_read = subparsers.add_parser("read", help="Read embedded metadata from a file")
    p_read.add_argument("file", help="Path to file")
    p_read.add_argument("--json", action="store_true", help="Output compact JSON")

    # Command: write
    p_write = subparsers.add_parser("write", help="Embed metadata into a file")
    p_write.add_argument("file", help="Path to file")
    p_write.add_argument("--doc-id", required=True, help="Canonical Document ID")
    p_write.add_argument("--type", help="Document type (e.g. faktura, paragon, contract)")
    p_write.add_argument("--date", help="Document date (YYYY-MM-DD)")
    p_write.add_argument("--amount", help="Financial amount")
    p_write.add_argument("--currency", default="PLN", help="Currency code (e.g. PLN, EUR, USD)")
    p_write.add_argument("--contractor", help="Contractor / Vendor name")
    p_write.add_argument("--contractor-nip", help="Contractor Tax ID / NIP")
    p_write.add_argument("--category", default="koszty", help="Accounting category (e.g. koszty, przychody, bank, email)")
    p_write.add_argument("--title", help="Human-readable title")
    p_write.add_argument("--urn", help="Canonical Uniform Resource Name")
    p_write.add_argument("--country", default="PL", help="ISO country code (e.g. PL, DE, US)")
    p_write.add_argument("--city", help="City name (e.g. Szemud, Wejherowo, Gdansk)")
    p_write.add_argument("--address", help="Physical address")
    p_write.add_argument("--node", help="Distributed node name (e.g. lenovo, nvidia)")
    p_write.add_argument("--calc-hash", action="store_true", help="Compute SHA256 digest of source file into metadata")
    p_write.add_argument("--json-data", help="Raw JSON string with complete metadata payload")

    # Command: check
    p_check = subparsers.add_parser("check", help="Check MIME support and embedded metadata presence")
    p_check.add_argument("file", help="Path to file")

    # Command: validate
    p_val = subparsers.add_parser("validate", help="Validate embedded metadata and event log against official schemas")
    p_val.add_argument("file", help="Path to file")
    p_val.add_argument("--check-hash", action="store_true", help="Verify SHA256 integrity digest")
    p_val.add_argument("--json", action="store_true", help="Output validation report as JSON")

    # Command: history
    p_hist = subparsers.add_parser("history", help="Read embedded append-only event stream")
    p_hist.add_argument("file", help="Path to file")
    p_hist.add_argument("--json", action="store_true", help="Output JSON array instead of JSONL")

    # Command: append
    p_app = subparsers.add_parser("append", help="Append a discrete lifecycle event line (JSONL) to file")
    p_app.add_argument("file", help="Path to file")
    p_app.add_argument("--event", "--event-type", dest="event", required=True, help="Event name (e.g. scanned, staged, routed, synced, classified)")
    p_app.add_argument("--doc-id", dest="doc_id", help="Canonical Document ID (inferred from file if omitted)")
    p_app.add_argument("--node", help="Cluster node identifier (e.g. lenovo, nvidia)")
    p_app.add_argument("--actor", help="Actor or agent identifier")
    p_app.add_argument("--delta", "--payload", dest="delta", help="JSON string representing modified attributes")

    args = parser.parse_args(argv)

    if args.command == "validate":
        path = Path(args.file)
        res = validate_file(path, check_hash=args.check_hash)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            if res["valid"]:
                print(f"VALID: {res['file']} (docId={res.get('docId')}, mime={res.get('mime')}, events={res.get('eventsCount')})")
            else:
                print(f"INVALID: {res['file']} ({len(res['errors'])} errors):", file=sys.stderr)
                for err in res["errors"]:
                    print(f"  - {err}", file=sys.stderr)
            if res.get("warnings"):
                print("Warnings:")
                for w in res["warnings"]:
                    print(f"  * {w}")
        return 0 if res["valid"] else (2 if not res.get("hasMetadata") else 1)

    elif args.command == "history":
        path = Path(args.file)
        if not path.is_file():
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 1
        events = read_events(path)
        if not events:
            print(f"No embedded event history found in {path}", file=sys.stderr)
            return 2
        if args.json:
            print(json.dumps([ev.to_dict() for ev in events], indent=2, ensure_ascii=False))
        else:
            for ev in events:
                print(ev.to_jsonl())
        return 0

    elif args.command == "append":
        path = Path(args.file)
        if not path.is_file():
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 1

        doc_id = args.doc_id
        if not doc_id:
            existing = read_metafile(path)
            if existing and existing.docId:
                doc_id = existing.docId
            else:
                print(f"Error: --doc-id is required when file has no existing embedded metadata", file=sys.stderr)
                return 1

        delta = {}
        if args.delta:
            try:
                delta = json.loads(args.delta)
            except Exception as e:
                print(f"Error parsing --delta JSON: {e}", file=sys.stderr)
                return 1

        event = MetafileEvent(
            event=args.event,
            docId=doc_id,
            node=args.node,
            actor=args.actor,
            delta=delta,
        )
        ok = append_event(path, event)
        if ok:
            print(f"Successfully appended event '{args.event}' to {path}")
            return 0
        else:
            print(f"Failed to append event to {path}", file=sys.stderr)
            return 3

    elif args.command == "read":
        path = Path(args.file)
        if not path.is_file():
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 1
        meta = read_metafile(path)
        if not meta:
            print(f"No wellmanifest metadata found embedded in {path}", file=sys.stderr)
            return 2
        if args.json:
            print(meta.to_json(indent=None))
        else:
            print(meta.to_json(indent=2))
        return 0

    elif args.command == "write":
        path = Path(args.file)
        if not path.is_file():
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 1

        if args.json_data:
            meta = Metafile.from_json(args.json_data)
        else:
            meta = Metafile(
                docId=args.doc_id,
                type=args.type,
                date=args.date,
                currency=args.currency or "PLN",
            )
            if args.amount:
                meta.accounting.amount = args.amount
            if args.currency:
                meta.accounting.currency = args.currency
            if args.contractor:
                meta.accounting.contractor = args.contractor
            if args.contractor_nip:
                meta.accounting.contractorNip = args.contractor_nip
            if args.category:
                meta.accounting.category = args.category
            if args.title:
                meta.title = args.title
            if args.urn:
                meta.urn = args.urn
            if args.country:
                meta.location.country = args.country
            if args.city:
                meta.location.city = args.city
            if args.address:
                meta.location.address = args.address
            if args.node:
                meta.location.node = args.node

            if args.calc_hash:
                raw_bytes = path.read_bytes()
                meta.hashes.sha256 = hashlib.sha256(raw_bytes).hexdigest()

        ok = write_metafile(path, meta)
        if ok:
            print(f"Successfully embedded metafile {meta.docId} into {path} ({detect_mime(path)})")
            return 0
        else:
            print(f"Failed to embed metafile into {path}", file=sys.stderr)
            return 3

    elif args.command == "check":
        path = Path(args.file)
        mime = detect_mime(path)
        supported = supports_mime(path)
        meta = read_metafile(path) if supported else None
        res = {
            "file": str(path),
            "mime": mime,
            "supported": supported,
            "hasEmbeddedMetadata": meta is not None,
            "docId": meta.docId if meta else None,
        }
        print(json.dumps(res, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
