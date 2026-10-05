"""Unit tests for wellmanifest-metafile."""
import io
import json
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from wellmanifest_metafile.core import Metafile
from wellmanifest_metafile.detector import read_metafile, write_metafile, detect_mime
from wellmanifest_metafile.adapters.pdf import write_pdf_metafile, read_pdf_metafile
from wellmanifest_metafile.adapters.png import write_png_metafile, read_png_metafile
from wellmanifest_metafile.adapters.jpeg import write_jpeg_metafile, read_jpeg_metafile
from wellmanifest_metafile.adapters.eml import write_eml_metafile, read_eml_metafile
from wellmanifest_metafile.adapters.text import write_text_metafile, read_text_metafile


def test_metafile_serialization():
    meta = Metafile(
        docId="DOC-TEST-1234",
        type="faktura",
        date="2026-09-07",
        currency="PLN",
    )
    meta.accounting.amount = "250.00"
    meta.accounting.contractor = "BOTERM"
    meta.accounting.currency = "PLN"
    meta.location.country = "PL"
    meta.location.city = "Szemud"
    meta.location.address = "ul. Wejherowska 11"
    meta.location.node = "lenovo"
    meta.ocr.text = "FAKTURA VAT"

    d = meta.to_dict()
    assert d["docId"] == "DOC-TEST-1234"
    assert d["schema"] == "wellmanifest.metafile/v1"
    assert d["currency"] == "PLN"
    assert d["accounting"]["amount"] == "250.00"
    assert d["accounting"]["contractor"] == "BOTERM"
    assert d["location"]["city"] == "Szemud"
    assert d["location"]["country"] == "PL"
    assert d["location"]["node"] == "lenovo"

    recovered = Metafile.from_dict(d)
    assert recovered.docId == "DOC-TEST-1234"
    assert recovered.currency == "PLN"
    assert recovered.accounting.amount == "250.00"
    assert recovered.accounting.contractor == "BOTERM"
    assert recovered.location.city == "Szemud"
    assert recovered.location.country == "PL"
    assert recovered.location.node == "lenovo"


def test_png_embedding(tmp_path):
    png_path = tmp_path / "test.png"
    img = Image.new("RGB", (100, 100), color="white")
    img.save(png_path, "PNG")

    meta = Metafile(
        docId="DOC-PNG-001",
        type="paragon",
        date="2026-10-01",
    )
    meta.accounting.amount = "42.50"
    meta.accounting.contractor = "BIEDRONKA"

    assert write_png_metafile(png_path, meta) is True

    read_back = read_png_metafile(png_path)
    assert read_back is not None
    assert read_back.docId == "DOC-PNG-001"
    assert read_back.accounting.amount == "42.50"
    assert read_back.accounting.contractor == "BIEDRONKA"


def test_jpeg_embedding(tmp_path):
    jpg_path = tmp_path / "test.jpg"
    img = Image.new("RGB", (100, 100), color="blue")
    img.save(jpg_path, "JPEG")

    meta = Metafile(
        docId="DOC-JPG-002",
        type="faktura",
        date="2026-09-15",
    )
    meta.accounting.amount = "120.00"
    meta.accounting.contractor = "ORLEN"

    assert write_jpeg_metafile(jpg_path, meta) is True

    read_back = read_jpeg_metafile(jpg_path)
    assert read_back is not None
    assert read_back.docId == "DOC-JPG-002"
    assert read_back.accounting.amount == "120.00"
    assert read_back.accounting.contractor == "ORLEN"


def test_pdf_embedding(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    # Create minimal valid PDF
    pdf_bytes = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 100 100] >> endobj\n"
        b"xref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n"
        b"trailer << /Size 4 /Root 1 0 R >>\n"
        b"startxref\n185\n%%EOF\n"
    )
    pdf_path.write_bytes(pdf_bytes)

    meta = Metafile(
        docId="DOC-PDF-003",
        type="faktura",
        date="2026-09-07",
    )
    meta.accounting.amount = "250.00"
    meta.accounting.contractor = "BOTERM"

    assert write_pdf_metafile(pdf_path, meta) is True

    read_back = read_pdf_metafile(pdf_path)
    assert read_back is not None
    assert read_back.docId == "DOC-PDF-003"
    assert read_back.accounting.contractor == "BOTERM"
    assert read_back.accounting.amount == "250.00"


def test_eml_embedding(tmp_path):
    eml_path = tmp_path / "test.eml"
    eml_path.write_text(
        "From: test@example.com\nTo: user@example.com\nSubject: Invoice\n\nPlease find attached.",
        encoding="utf-8"
    )

    meta = Metafile(
        docId="DOC-EML-004",
        type="faktura",
        date="2026-10-05",
    )
    meta.accounting.amount = "500.00"
    meta.accounting.contractor = "GOOGLE"

    assert write_eml_metafile(eml_path, meta) is True

    read_back = read_eml_metafile(eml_path)
    assert read_back is not None
    assert read_back.docId == "DOC-EML-004"
    assert read_back.accounting.amount == "500.00"
    assert read_back.accounting.contractor == "GOOGLE"


def test_markdown_embedding(tmp_path):
    md_path = tmp_path / "test.md"
    md_path.write_text("# My Invoice\n\nSome notes here.", encoding="utf-8")

    meta = Metafile(
        docId="DOC-MD-005",
        type="notatka",
        date="2026-10-05",
    )
    meta.accounting.amount = "99.00"

    assert write_text_metafile(md_path, meta) is True

    read_back = read_text_metafile(md_path)
    assert read_back is not None
    assert read_back.docId == "DOC-MD-005"
    assert read_back.accounting.amount == "99.00"


def test_dispatcher(tmp_path):
    png_path = tmp_path / "auto.png"
    Image.new("RGB", (50, 50)).save(png_path, "PNG")

    meta = Metafile(docId="DOC-AUTO-006")
    meta.accounting.contractor = "DISPATCHER"

    assert write_metafile(png_path, meta) is True
    res = read_metafile(png_path)
    assert res is not None
    assert res.docId == "DOC-AUTO-006"
    assert res.accounting.contractor == "DISPATCHER"


def test_event_stream_and_folding(tmp_path):
    from wellmanifest_metafile.events import MetafileEvent, fold_events, append_pdf_event, read_pdf_events

    pdf_path = tmp_path / "stream_test.pdf"
    pdf_bytes = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 100 100] >> endobj\n"
        b"xref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n"
        b"trailer << /Size 4 /Root 1 0 R >>\n"
        b"startxref\n185\n%%EOF\n"
    )
    pdf_path.write_bytes(pdf_bytes)

    # 1. Event: scanned
    ev1 = MetafileEvent(
        event="scanned",
        docId="DOC-STREAM-001",
        node="android-bbf100",
        delta={"type": "faktura", "date": "2026-09-07"}
    )
    assert append_pdf_event(pdf_path, ev1) is True

    # 2. Event: ocr_extracted
    ev2 = MetafileEvent(
        event="ocr_extracted",
        docId="DOC-STREAM-001",
        actor="paddle-ocr",
        delta={"accounting": {"amount": "250.00", "contractor": "BOTERM"}}
    )
    assert append_pdf_event(pdf_path, ev2) is True

    # 3. Event: routed
    ev3 = MetafileEvent(
        event="routed",
        docId="DOC-STREAM-001",
        node="nvidia",
        delta={"location": {"node": "lenovo", "city": "Szemud"}}
    )
    assert append_pdf_event(pdf_path, ev3) is True

    # Read back events
    history = read_pdf_events(pdf_path)
    assert len(history) == 3
    assert history[0].event == "scanned"
    assert history[1].event == "ocr_extracted"
    assert history[2].event == "routed"

    # Reduce / Fold to current state
    current = fold_events(history)
    assert current is not None
    assert current.docId == "DOC-STREAM-001"
    assert current.type == "faktura"
    assert current.date == "2026-09-07"
    assert current.accounting.amount == "250.00"
    assert current.accounting.contractor == "BOTERM"
    assert current.location.city == "Szemud"
    assert current.provenance.extra.get("lastEvent") == "routed" or current.to_dict()["provenance"].get("lastEvent") == "routed"
