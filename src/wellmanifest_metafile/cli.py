"""CLI interface for wellmanifest-metafile."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import Metafile
from .detector import read_metafile, write_metafile, supports_mime, detect_mime


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
    p_write.add_argument("--country", default="PL", help="ISO country code (e.g. PL, DE, US)")
    p_write.add_argument("--city", help="City name (e.g. Szemud, Wejherowo, Gdansk)")
    p_write.add_argument("--address", help="Physical address")
    p_write.add_argument("--node", help="Distributed node name (e.g. lenovo, nvidia)")
    p_write.add_argument("--json-data", help="Raw JSON string with complete metadata payload")

    # Command: check
    p_check = subparsers.add_parser("check", help="Check MIME support and embedded metadata presence")
    p_check.add_argument("file", help="Path to file")

    args = parser.parse_args(argv)

    if args.command == "read":
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
            if args.country:
                meta.location.country = args.country
            if args.city:
                meta.location.city = args.city
            if args.address:
                meta.location.address = args.address
            if args.node:
                meta.location.node = args.node

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
