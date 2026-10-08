"""Tests for the metafile command-line interface (CLI)."""
from __future__ import annotations

import json
from pathlib import Path
import pytest
from pypdf import PdfWriter

from wellmanifest_metafile.cli import main


def test_cli_full_lifecycle(tmp_path: Path, capsys):
    sample_pdf = tmp_path / "invoice.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with open(sample_pdf, "wb") as f:
        writer.write(f)

    # 1. Check initially empty
    rc = main(["check", str(sample_pdf)])
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["hasEmbeddedMetadata"] is False

    # 2. Write metadata
    rc = main([
        "write", str(sample_pdf),
        "--doc-id", "DOC-CLI-999",
        "--type", "faktura",
        "--date", "2026-10-08",
        "--amount", "450.00",
        "--currency", "PLN",
        "--contractor", "ORLEN",
        "--category", "koszty",
        "--city", "Szemud",
    ])
    assert rc == 0
    capsys.readouterr()

    # 3. Read metadata
    rc = main(["read", str(sample_pdf), "--json"])
    assert rc == 0
    read_out = capsys.readouterr().out
    read_meta = json.loads(read_out)
    assert read_meta["docId"] == "DOC-CLI-999"
    assert read_meta["accounting"]["amount"] == "450.00"
    assert read_meta["accounting"]["contractor"] == "ORLEN"
    assert read_meta["location"]["city"] == "Szemud"

    # 4. Append lifecycle event using README syntax (--event-type, --payload, auto doc-id)
    rc = main([
        "append", str(sample_pdf),
        "--event-type", "classified",
        "--actor", "accountant",
        "--payload", json.dumps({"accounting": {"category": "inne", "amount": "450.00"}}),
    ])
    assert rc == 0
    capsys.readouterr()

    # 5. History JSON output
    rc = main(["history", str(sample_pdf), "--json"])
    assert rc == 0
    hist_out = capsys.readouterr().out
    hist = json.loads(hist_out)
    assert len(hist) == 1
    assert hist[0]["event"] == "classified"
    assert hist[0]["actor"] == "accountant"
    assert hist[0]["docId"] == "DOC-CLI-999"

    # 6. Read state after event folding
    rc = main(["read", str(sample_pdf), "--json"])
    assert rc == 0
    folded_out = capsys.readouterr().out
    folded_meta = json.loads(folded_out)
    assert folded_meta["accounting"]["category"] == "inne"
    assert folded_meta["provenance"]["lastEvent"] == "classified"

    # 7. Validate
    rc = main(["validate", str(sample_pdf), "--json"])
    assert rc == 0
    val_out = capsys.readouterr().out
    val_res = json.loads(val_out)
    assert val_res["valid"] is True
    assert val_res["docId"] == "DOC-CLI-999"
    assert val_res["eventsCount"] == 1
    assert val_res["errors"] == []


def test_cli_validate_failures(tmp_path: Path, capsys):
    # Non-existent file
    rc = main(["validate", str(tmp_path / "ghost.pdf")])
    assert rc == 2
    capsys.readouterr()

    # File without metadata
    empty_pdf = tmp_path / "blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=10, height=10)
    with open(empty_pdf, "wb") as f:
        writer.write(f)

    rc = main(["validate", str(empty_pdf)])
    assert rc == 2
    err_out = capsys.readouterr().err
    assert "No embedded wellmanifest metadata found" in err_out
