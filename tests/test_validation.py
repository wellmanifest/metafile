"""Unit tests for Metafile schema validation and conformance verification."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from pypdf import PdfWriter

from wellmanifest_metafile.core import Metafile, AccountingMeta, LocationMeta, HashesMeta
from wellmanifest_metafile.events import MetafileEvent
from wellmanifest_metafile.detector import write_metafile
from wellmanifest_metafile.validator import validate_metafile, validate_event, validate_file


def test_validate_valid_metafile():
    meta = Metafile(
        docId="DOC-2026-VAL-001",
        schema="wellmanifest.metafile/v1",
        currency="PLN",
        accounting=AccountingMeta(
            amount="1234.56",
            currency="PLN",
            category="koszty",
            contractor="ACME SP Z OO",
            contractorNip="1234567890",
            period="2026.10",
        ),
        location=LocationMeta(
            country="PL",
            city="Warszawa",
            node="nvidia",
        ),
        hashes=HashesMeta(
            sha256="a" * 64,
        ),
    )
    is_valid, errors = validate_metafile(meta)
    assert is_valid is True
    assert errors == []

    # Also test instance method .validate()
    method_valid, method_errors = meta.validate()
    assert method_valid is True
    assert method_errors == []


def test_validate_invalid_doc_id():
    meta = Metafile(docId="INVALID DOC ID WITH SPACES / SLASHES ?!")
    is_valid, errors = validate_metafile(meta)
    assert is_valid is False
    assert any("[docId]" in err for err in errors)


def test_validate_invalid_currency():
    meta = Metafile(docId="DOC-1", currency="POLISH_ZLOTY")
    is_valid, errors = validate_metafile(meta)
    assert is_valid is False
    assert any("[currency]" in err for err in errors)


def test_validate_invalid_amount_pattern():
    meta = Metafile(docId="DOC-1")
    meta.accounting.amount = "12.345"  # Only 2 decimal digits allowed
    is_valid, errors = validate_metafile(meta)
    assert is_valid is False
    assert any("[accounting.amount]" in err for err in errors)


def test_validate_invalid_category_enum():
    meta = Metafile(docId="DOC-1")
    meta.accounting.category = "non_existent_category"
    is_valid, errors = validate_metafile(meta)
    assert is_valid is False
    assert any("[accounting.category]" in err for err in errors)


def test_validate_invalid_sha256_hash():
    meta = Metafile(docId="DOC-1")
    meta.hashes.sha256 = "not_a_valid_64_hex_hash"
    is_valid, errors = validate_metafile(meta)
    assert is_valid is False
    assert any("[hashes.sha256]" in err for err in errors)


def test_validate_event_valid_and_invalid():
    # Valid event
    ev = MetafileEvent(
        event="staged",
        docId="DOC-TEST-EV",
        v=1,
        actor="scanner",
        node="node-1",
        delta={"accounting": {"amount": "100.00"}},
    )
    is_valid, errors = validate_event(ev)
    assert is_valid is True
    assert errors == []

    # Instance method
    assert ev.validate() == (True, [])

    # Invalid version
    ev_bad_v = MetafileEvent(
        event="staged",
        docId="DOC-TEST-EV",
        v=2,
    )
    is_valid_bad, errors_bad = validate_event(ev_bad_v)
    assert is_valid_bad is False
    assert any("[v]" in err for err in errors_bad)


def test_validate_file_workflow(tmp_path: Path):
    # 1. Non-existent file
    res_none = validate_file(tmp_path / "does_not_exist.pdf")
    assert res_none["valid"] is False
    assert "File not found" in res_none["errors"][0]

    # 2. File without metadata
    pdf_path = tmp_path / "test.pdf"
    w = PdfWriter()
    w.add_blank_page(width=50, height=50)
    with open(pdf_path, "wb") as f:
        w.write(f)

    res_empty = validate_file(pdf_path)
    assert res_empty["valid"] is False
    assert res_empty["hasMetadata"] is False

    # 3. File with valid metadata
    meta = Metafile(
        docId="DOC-PDF-VALID-01",
        accounting=AccountingMeta(amount="75.00", currency="PLN", category="koszty"),
    )
    write_metafile(pdf_path, meta)

    res_valid = validate_file(pdf_path)
    assert res_valid["valid"] is True
    assert res_valid["hasMetadata"] is True
    assert res_valid["docId"] == "DOC-PDF-VALID-01"
    assert res_valid["errors"] == []
