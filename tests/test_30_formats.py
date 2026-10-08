"""Comprehensive test suite for 30 most popular data, graphic, audio, and video formats."""
from __future__ import annotations

import json
import subprocess
import wave
import zipfile
from pathlib import Path

import pytest
from PIL import Image

from wellmanifest_metafile.core import Metafile, AccountingMeta, LocationMeta
from wellmanifest_metafile.detector import read_metafile, write_metafile, supports_mime, detect_mime


def make_test_meta(fmt_name: str) -> Metafile:
    return Metafile(
        docId=f"DOC-TEST-30-{fmt_name.upper()}",
        schema="wellmanifest.metafile/v1",
        type="test_document",
        date="2026-10-05",
        accounting=AccountingMeta(
            amount="350.00",
            currency="PLN",
            contractor=f"CONTRACTOR-{fmt_name.upper()}",
            category="koszty",
            subfolder="koszty",
        ),
        location=LocationMeta(
            country="PL",
            city="Warszawa",
            address="ul. Marszałkowska 10",
            postalCode="00-001",
            node="nvidia",
        ),
    )


def assert_meta_matches(meta: Metafile, fmt_name: str):
    assert meta is not None, f"Failed to read meta for {fmt_name}"
    assert meta.docId == f"DOC-TEST-30-{fmt_name.upper()}"
    assert meta.accounting is not None
    assert meta.accounting.amount == "350.00"
    assert meta.accounting.currency == "PLN"
    assert meta.accounting.contractor == f"CONTRACTOR-{fmt_name.upper()}"
    assert meta.location is not None
    assert meta.location.city == "Warszawa"
    assert meta.location.country == "PL"
    is_valid, errs = meta.validate()
    assert is_valid, f"Schema validation error in {fmt_name}: {errs}"


# ==============================================================================
# 1. Structured Data & Documents (11 Formats)
# ==============================================================================

def test_format_pdf(tmp_path: Path):
    from pypdf import PdfWriter
    path = tmp_path / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with open(path, "wb") as f:
        writer.write(f)

    meta = make_test_meta("pdf")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "pdf")


def test_format_json(tmp_path: Path):
    path = tmp_path / "sample.json"
    path.write_text(json.dumps({"app": "demo", "version": "1.0"}), encoding="utf-8")

    meta = make_test_meta("json")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "json")
    # Verify primary JSON content is preserved
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["app"] == "demo"


def test_format_jsonl(tmp_path: Path):
    path = tmp_path / "sample.jsonl"
    path.write_text('{"event": "login", "user": "tom"}\n{"event": "action"}\n', encoding="utf-8")

    meta = make_test_meta("jsonl")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "jsonl")


def test_format_xml(tmp_path: Path):
    path = tmp_path / "sample.xml"
    path.write_text('<?xml version="1.0" encoding="utf-8"?>\n<catalog><item id="1">Doc</item></catalog>', encoding="utf-8")

    meta = make_test_meta("xml")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "xml")


def test_format_csv(tmp_path: Path):
    path = tmp_path / "sample.csv"
    path.write_text("id,name,value\n1,Alpha,100\n2,Beta,200\n", encoding="utf-8")

    meta = make_test_meta("csv")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "csv")


def test_format_tsv(tmp_path: Path):
    path = tmp_path / "sample.tsv"
    path.write_text("id\tname\tvalue\n1\tAlpha\t100\n", encoding="utf-8")

    meta = make_test_meta("tsv")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "tsv")


def test_format_yaml(tmp_path: Path):
    path = tmp_path / "sample.yaml"
    path.write_text("server:\n  host: 127.0.0.1\n  port: 8080\n", encoding="utf-8")

    meta = make_test_meta("yaml")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "yaml")


def test_format_markdown(tmp_path: Path):
    path = tmp_path / "sample.md"
    path.write_text("# Project Title\n\nSome important markdown notes.\n", encoding="utf-8")

    meta = make_test_meta("md")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "md")


def test_format_text(tmp_path: Path):
    path = tmp_path / "sample.txt"
    path.write_text("Raw plain text document contents.\n", encoding="utf-8")

    meta = make_test_meta("txt")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "txt")


def test_format_html(tmp_path: Path):
    path = tmp_path / "sample.html"
    path.write_text("<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Hello</h1></body></html>", encoding="utf-8")

    meta = make_test_meta("html")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "html")


def test_format_eml(tmp_path: Path):
    path = tmp_path / "sample.eml"
    path.write_text("From: test@example.com\nTo: admin@example.com\nSubject: Invoice\n\nPlease find attached.", encoding="utf-8")

    meta = make_test_meta("eml")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "eml")


# ==============================================================================
# 2. Archives & Office Documents (3 Formats)
# ==============================================================================

def test_format_zip(tmp_path: Path):
    path = tmp_path / "sample.zip"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("test.txt", "Inside archive")

    meta = make_test_meta("zip")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "zip")
    with zipfile.ZipFile(path, "r") as zf:
        assert zf.read("test.txt") == b"Inside archive"


def test_format_docx(tmp_path: Path):
    path = tmp_path / "sample.docx"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("word/document.xml", "<w:document/>")

    meta = make_test_meta("docx")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "docx")
    with zipfile.ZipFile(path, "r") as zf:
        assert zf.read("word/document.xml") == b"<w:document/>"


def test_format_xlsx(tmp_path: Path):
    path = tmp_path / "sample.xlsx"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("xl/workbook.xml", "<workbook/>")

    meta = make_test_meta("xlsx")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "xlsx")
    with zipfile.ZipFile(path, "r") as zf:
        assert zf.read("xl/workbook.xml") == b"<workbook/>"


# ==============================================================================
# 3. Graphics & Images (9 Formats)
# ==============================================================================

def test_format_png(tmp_path: Path):
    path = tmp_path / "sample.png"
    Image.new("RGB", (10, 10), color="red").save(path, format="PNG")

    meta = make_test_meta("png")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "png")
    with Image.open(path) as img:
        assert img.size == (10, 10)


def test_format_jpeg(tmp_path: Path):
    path = tmp_path / "sample.jpg"
    Image.new("RGB", (10, 10), color="green").save(path, format="JPEG")

    meta = make_test_meta("jpeg")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "jpeg")
    with Image.open(path) as img:
        assert img.size == (10, 10)


def test_format_webp(tmp_path: Path):
    path = tmp_path / "sample.webp"
    Image.new("RGB", (10, 10), color="blue").save(path, format="WEBP")

    meta = make_test_meta("webp")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "webp")


def test_format_svg(tmp_path: Path):
    path = tmp_path / "sample.svg"
    path.write_text('<svg viewBox="0 0 10 10"><rect width="10" height="10"/></svg>', encoding="utf-8")

    meta = make_test_meta("svg")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "svg")


def test_format_gif(tmp_path: Path):
    path = tmp_path / "sample.gif"
    Image.new("RGB", (10, 10), color="yellow").save(path, format="GIF")

    meta = make_test_meta("gif")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "gif")


def test_format_tiff(tmp_path: Path):
    path = tmp_path / "sample.tiff"
    Image.new("RGB", (10, 10), color="white").save(path, format="TIFF")

    meta = make_test_meta("tiff")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "tiff")


def test_format_bmp(tmp_path: Path):
    path = tmp_path / "sample.bmp"
    Image.new("RGB", (10, 10), color="purple").save(path, format="BMP")

    meta = make_test_meta("bmp")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "bmp")


def test_format_ico(tmp_path: Path):
    path = tmp_path / "sample.ico"
    Image.new("RGB", (16, 16), color="cyan").save(path, format="ICO")

    meta = make_test_meta("ico")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "ico")


def test_format_avif(tmp_path: Path):
    path = tmp_path / "sample.avif"
    # Create valid dummy AVIF container or byte sequence
    path.write_bytes(b"\x00\x00\x00\x1cftypavif\x00\x00\x00\x00avifmif1miafMA1B")

    meta = make_test_meta("avif")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "avif")


# ==============================================================================
# 4. Audio (4 Formats)
# ==============================================================================

def test_format_mp3(tmp_path: Path):
    path = tmp_path / "sample.mp3"
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=0.1", "-c:a", "libmp3lame", str(path)], capture_output=True, check=True)

    meta = make_test_meta("mp3")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "mp3")


def test_format_wav(tmp_path: Path):
    path = tmp_path / "sample.wav"
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(b"\x00\x00" * 200)

    meta = make_test_meta("wav")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "wav")


def test_format_flac(tmp_path: Path):
    path = tmp_path / "sample.flac"
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=0.1", "-c:a", "flac", str(path)], capture_output=True, check=True)

    meta = make_test_meta("flac")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "flac")


def test_format_ogg(tmp_path: Path):
    path = tmp_path / "sample.ogg"
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=0.1", "-c:a", "libvorbis", str(path)], capture_output=True, check=True)

    meta = make_test_meta("ogg")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "ogg")


# ==============================================================================
# 5. Video (3 Formats)
# ==============================================================================

def test_format_mp4(tmp_path: Path):
    path = tmp_path / "sample.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=black:size=16x16:rate=1:duration=0.1", "-c:v", "libx264", str(path)], capture_output=True, check=True)

    meta = make_test_meta("mp4")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "mp4")


def test_format_mkv(tmp_path: Path):
    path = tmp_path / "sample.mkv"
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=black:size=16x16:rate=1:duration=0.1", str(path)], capture_output=True, check=True)

    meta = make_test_meta("mkv")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "mkv")


def test_format_webm(tmp_path: Path):
    path = tmp_path / "sample.webm"
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=black:size=16x16:rate=1:duration=0.1", str(path)], capture_output=True, check=True)

    meta = make_test_meta("webm")
    write_metafile(path, meta)
    read_meta = read_metafile(path)
    assert_meta_matches(read_meta, "webm")
