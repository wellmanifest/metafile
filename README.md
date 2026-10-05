# wellmanifest/metafile

> **Universal Standard for Self-Contained Embedded Document Metadata**

`wellmanifest/metafile` defines the canonical specification and reference implementation for embedding structured, tamper-evident metadata directly into source files (PDF, PNG, JPEG, WebP, TIFF, SVG, EML, Markdown, Audio, Video, Archives).

---

## 1. Motivation & Principles

Historically, accounting, document archival, and automation systems relied on **sidecar files** (`.pdf.json`, `.source.yaml`). Sidecars suffer from critical architectural weaknesses:
- **Fragmentation:** Moving, emailing, or uploading the primary artifact (`.pdf`) strips the metadata unless packed together.
- **File System Clutter:** Thousands of paired JSON files double inode counts and complicate folder navigation.
- **Drift:** Sidecars can be edited or deleted independently, breaking cryptographic and accounting invariants.

### The Metafile Principles
1. **100% Self-Contained Artifacts:** Every file carries its identity (`docId`), financial fields, OCR text, and cryptographic digests inside its native container format.
2. **Lossless & Non-Destructive:** Metadata embedding MUST conform to official ISO/W3C/IETF standards and MUST NOT corrupt visual, audio, or textual rendering.
3. **Per-MIME Standards:** Each file format uses its respective native standard (XMP in PDF/JPEG, `iTXt` in PNG, `X-` headers in EML, YAML frontmatter in Markdown).
4. **Deterministic URN & Hash Anchoring:** Every file embeds canonical URNs (`urn:fin:doc:...`) and sha256/dhash/phash digests.

---

## 2. Supported MIME Types & Specifications (Top 30 Formats)

Specifications are organized into dedicated folders per MIME type under [`spec/mime-types/`](spec/mime-types/):

| MIME Category | MIME Type | Extensions | Embedded Location | Spec Link |
|---|---|---|---|---|
| **Document** | `application/pdf` | `.pdf` | `/Info`, XMP `/Metadata`, `/EmbeddedFiles` | [PDF Spec](spec/mime-types/application/pdf/README.md) |
| **Data** | `application/json` | `.json` | `$metafile` root property | [JSON Spec](spec/mime-types/application/json/README.md) |
| **Data Stream** | `application/x-ndjson` | `.jsonl, .ndjson` | `# wellmanifest:` comment header / record | [JSONL Spec](spec/mime-types/application/x-ndjson/README.md) |
| **Markup** | `application/xml` | `.xml` | `<metadata id="wellmanifest-metafile">` | [XML Spec](spec/mime-types/application/xml/README.md) |
| **Tabular** | `text/csv` | `.csv` | Leading `# wellmanifest:` comment header | [CSV Spec](spec/mime-types/text/csv/README.md) |
| **Tabular** | `text/tab-separated-values` | `.tsv` | Leading `# wellmanifest:` comment header | [TSV Spec](spec/mime-types/text/tab-separated-values/README.md) |
| **Config/Data**| `application/yaml` | `.yaml, .yml` | `_metafile` root key / frontmatter | [YAML Spec](spec/mime-types/application/yaml/README.md) |
| **Document** | `text/markdown` | `.md, .markdown` | YAML Frontmatter (`---`) | [Markdown Spec](spec/mime-types/text/markdown/README.md) |
| **Text** | `text/plain` | `.txt` | Header / Trailing metadata block | [Plain Text Spec](spec/mime-types/text/plain/README.md) |
| **Web Page** | `text/html` | `.html, .htm` | `<script type="application/ld+json" id="wellmanifest-metafile">` | [HTML Spec](spec/mime-types/text/html/README.md) |
| **Email** | `message/rfc822` | `.eml, .msg` | RFC 5322 `X-Wellmanifest-*` headers | [EML Spec](spec/mime-types/message/rfc822/README.md) |
| **Archive** | `application/zip` | `.zip` | `META-INF/metafile.json` / ZIP comment | [ZIP Spec](spec/mime-types/application/zip/README.md) |
| **E-Book** | `application/epub+zip`| `.epub` | `META-INF/metafile.json` / OPF `<metadata>` | [EPUB Spec](spec/mime-types/application/epub+zip/README.md) |
| **Office Doc** | `application/vnd.openxmlformats` | `.docx` | `META-INF/metafile.json` in OOXML package | [OOXML Spec](spec/mime-types/application/vnd.openxmlformats/README.md) |
| **Office Sheet**| `application/vnd.openxmlformats` | `.xlsx` | `META-INF/metafile.json` in OOXML package | [OOXML Spec](spec/mime-types/application/vnd.openxmlformats/README.md) |
| **Raster Image** | `image/png` | `.png` | `iTXt` chunk (`wellmanifest:metafile`) | [PNG Spec](spec/mime-types/image/png/README.md) |
| **Raster Image** | `image/jpeg` | `.jpg, .jpeg` | APP1 (XMP packet) / EXIF Tag 0x9286 | [JPEG Spec](spec/mime-types/image/jpeg/README.md) |
| **Web Image** | `image/webp` | `.webp` | RIFF `'XMP '` / `'EXIF'` chunk | [WebP Spec](spec/mime-types/image/webp/README.md) |
| **Vector Image** | `image/svg+xml` | `.svg` | `<metadata id="wellmanifest-metafile">` | [SVG Spec](spec/mime-types/image/svg+xml/README.md) |
| **Animation** | `image/gif` | `.gif` | Application Extension block `comment` / XMP | [GIF Spec](spec/mime-types/image/gif/README.md) |
| **Print Image** | `image/tiff` | `.tiff, .tif` | TIFF Tag 700 (XMP) / Tag 37510 (UserComment) | [TIFF Spec](spec/mime-types/image/tiff/README.md) |
| **Bitmap** | `image/bmp` | `.bmp` | Non-destructive trailer block | [BMP Spec](spec/mime-types/image/bmp/README.md) |
| **Icon** | `image/x-icon` | `.ico` | Non-destructive trailer block | [ICO Spec](spec/mime-types/image/x-icon/README.md) |
| **Modern Image**| `image/avif` | `.avif, .heic`| ISOBMFF `meta` item (`mime`) / trailer | [AVIF Spec](spec/mime-types/image/avif/README.md) |
| **Audio** | `audio/mpeg` | `.mp3` | ID3v2.4 `TXXX:WELLMANIFEST_METAFILE` | [MP3 Spec](spec/mime-types/audio/mpeg/README.md) |
| **Audio** | `audio/flac` | `.flac` | Vorbis Comment `WELLMANIFEST_METAFILE` | [FLAC Spec](spec/mime-types/audio/flac/README.md) |
| **Audio** | `audio/ogg` | `.ogg, .oga` | Vorbis Comment `WELLMANIFEST_METAFILE` | [OGG Spec](spec/mime-types/audio/ogg/README.md) |
| **Audio** | `audio/wav` | `.wav` | RIFF `'id3 '` / `'INFO'` sub-chunks | [WAV Spec](spec/mime-types/audio/wav/README.md) |
| **Audio / Video**| `audio/mp4`, `video/mp4` | `.m4a, .mp4` | QuickTime atom `----:com.apple.iTunes:WELLMANIFEST_METAFILE` | [MP4 Spec](spec/mime-types/video/mp4/README.md) |
| **Video** | `video/x-matroska` | `.mkv` | EBML `Tags` element / trailer | [Matroska Spec](spec/mime-types/video/x-matroska/README.md) |
| **Video** | `video/webm` | `.webm` | EBML `Tags` element / trailer | [WebM Spec](spec/mime-types/video/webm/README.md) |

---

## 3. Schema Structure

All metadata conforms to [`schemas/metafile.v1.schema.json`](schemas/metafile.v1.schema.json):

```json
{
  "schema": "wellmanifest.metafile/v1",
  "docId": "DOC-FV-3A0C5BB3A175D4A4",
  "urn": "urn:fin:doc:faktura:2026.09:3a0c5bb3",
  "type": "faktura",
  "date": "2026-09-07",
  "accounting": {
    "amount": "250.00",
    "currency": "PLN",
    "contractor": "BOTERM",
    "contractorNip": "5891973148",
    "category": "koszty",
    "subfolder": "koszty"
  },
  "hashes": {
    "sha256": "83662c138b2bd739cd1c65c9ce527bb36650b88f888a0bd3279bd2e64ee62838",
    "dhash": "713179716b794961",
    "phash": "a057aa567e4a53b8"
  },
  "ocr": {
    "backend": "paddle",
    "chars": 746,
    "confidence": 0.96,
    "text": "FAKTURA nr 18054/SZE/26..."
  },
  "provenance": {
    "createdAt": "2026-10-05T17:45:00Z",
    "deviceId": "phone-android-bbf100",
    "host": "nvidia"
  },
  "location": {
    "country": "PL",
    "city": "Szczecin",
    "address": "ul. Przykładowa 12/4",
    "postalCode": "70-100",
    "node": "nvidia"
  }
}
```

---

## 4. Append-Only JSONL Event Stream & Cascading State (Audit Trail)

Instead of rewriting the monolithic JSON state upon every update, `wellmanifest/metafile` supports an **append-only event log (JSONL)** directly in the file (e.g., incremental PDF trailer blocks):

- Each update is written as an immutable `MetafileEvent` delta.
- State evaluation behaves like **CSS cascading rules**: later event properties override earlier ones (`fold_events`).
- Event schema: [`schemas/metafile.event.schema.json`](schemas/metafile.event.schema.json).

```jsonl
{"eventId":"01JB...","type":"created","timestamp":"2026-10-05T17:45:00Z","actor":"scanner-daemon","docId":"DOC-123","data":{"accounting":{"amount":"250.00","currency":"PLN","contractor":"BOTERM"}}}
{"eventId":"01JB...","type":"classified","timestamp":"2026-10-05T18:10:00Z","actor":"tom","data":{"accounting":{"category":"koszty","subfolder":"koszty"}}}
{"eventId":"01JB...","type":"approved","timestamp":"2026-10-05T18:30:00Z","actor":"ksiegowa","data":{"status":"approved"}}
```

---

## 5. Quick Start (Python CLI & Library)

```bash
# Install package
pip install -e /home/tom/github/wellmanifest/metafile

# Read embedded metadata from any supported file
metafile read faktura.pdf
metafile read paragon.png
metafile read invoice.eml

# Embed metadata directly into a file
metafile write faktura.pdf --doc-id "DOC-123" --amount "250.00" --currency "PLN" --contractor "BOTERM"

# Append a change event without rewriting existing data (audit log)
metafile append faktura.pdf --event-type "classified" --actor "ksiegowosc" --payload '{"accounting":{"category":"koszty"}}'

# Inspect complete revision history
metafile history faktura.pdf --json
```

---

## 6. Programmatic Python API

```python
from wellmanifest_metafile import Metafile, AccountingMeta, LocationMeta, read_metafile, write_metafile

# 1. Read metadata from any of the 30 supported formats
meta = read_metafile("faktura.pdf")
print(f"DocID: {meta.docId}, Amount: {meta.accounting.amount} {meta.accounting.currency}")
print(f"Location: {meta.location.city}, {meta.location.country}")

# 2. Write metadata into any file
meta_obj = Metafile(
    docId="DOC-2026-001",
    accounting=AccountingMeta(amount="499.00", currency="PLN", contractor="ACME CORP"),
    location=LocationMeta(country="PL", city="Warszawa", postalCode="00-001"),
)
write_metafile("scanned_receipt.png", meta_obj)
write_metafile("audio_note.mp3", meta_obj)
```

---

## 7. Automated Test Suite (30 Formats)

The specification and reference adapters are verified through automated end-to-end test suites:

```bash
# Run 30-format battery test suite
pytest tests/test_30_formats.py -v

# Run full project test suite
pytest tests/ -v
```

All 30 formats are tested for:
1. Valid binary/text file generation and integrity.
2. Lossless metadata embedding (`write_metafile`).
3. Lossless metadata extraction (`read_metafile`).
4. Financial and geographical field preservation (`accounting`, `location`).


