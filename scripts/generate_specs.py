#!/usr/bin/env python3
import os
from pathlib import Path

base = Path("/home/tom/github/wellmanifest/metafile/spec/mime-types")

specs = {
    "application/pdf": {
        "title": "application/pdf (Portable Document Format)",
        "exts": [".pdf"],
        "standard": "ISO 32000-1 / ISO 32000-2 / PDF/A-3 (ISO 19005-3) / XMP (ISO 16684-1)",
        "embedding": """### Embedding Strategies

1. **Document Information Dictionary (`/Info`)**:
   Standard dictionary at the trailer containing:
   - `/Title`: Human readable title
   - `/Subject`: Canonical `docId`
   - `/Keywords`: Comma-separated tags (contractor, amount, currency, URN)
   - Custom keys: `/WellmanifestDocId`, `/WellmanifestAmount`, `/WellmanifestContractor`

2. **Extensible Metadata Platform (`/Metadata` XMP Stream)**:
   ISO 16684-1 compliant RDF/XML packet embedded in the PDF Catalog (`/Root /Metadata`).
   Namespace: `xmlns:wm="https://wellmanifest.org/schemas/metafile/v1/"`
   Properties: `wm:docId`, `wm:urn`, `wm:accountingAmount`, `wm:contractor`, `wm:jsonPayload`

3. **Self-Contained Embedded File (`/EmbeddedFiles`)**:
   PDF/A-3 specification allowing the full raw `metafile.json` to be attached inside the PDF:
   - Name: `wellmanifest-metafile.json`
   - Relationship: `/AFRelationship /Supplement`
   - MIME: `application/json`""",
        "reading": """- Read `/Info` dict via standard PDF parser.
- Extract `/Metadata` stream and parse RDF/XML for `wm:*` attributes.
- Enumerate `/Names /EmbeddedFiles` for `wellmanifest-metafile.json` to obtain the complete lossless payload."""
    },
    "application/json": {
        "title": "application/json (JavaScript Object Notation)",
        "exts": [".json"],
        "standard": "RFC 8259",
        "embedding": """### Embedding Strategies

1. **Top-Level Envelope Property (`_metafile` or `$metafile`)**:
   In structured JSON objects, inject a reserved top-level key:
   ```json
   {
     "$metafile": {
       "schema": "wellmanifest.metafile/v1",
       "docId": "DOC-FV-3A0C5BB3A175D4A4",
       "accounting": { "amount": "250.00", "currency": "PLN" }
     },
     "data": { }
   }
   ```
2. **JSON-LD / Schema.org Context**:
   Use `@context: "https://wellmanifest.org/contexts/metafile/v1.jsonld"`""",
        "reading": """- Parse JSON AST and inspect root properties for `$metafile` or `_metafile`.
- Validate against `metafile.v1.schema.json`."""
    },
    "application/xml": {
        "title": "application/xml (Extensible Markup Language)",
        "exts": [".xml"],
        "standard": "W3C XML 1.0",
        "embedding": """### Embedding Strategies

1. **Processing Instruction or Header Comment**:
   `<?wellmanifest-metafile docId="DOC-123" amount="250.00" ?>`
   or: `<!-- wellmanifest:metafile:v1 {"docId": "DOC-123"} -->`
2. **Dedicated Child Element**:
   `<wm:metafile xmlns:wm="https://wellmanifest.org/schemas/metafile/v1/">...</wm:metafile>`""",
        "reading": """- XPath search for `//wm:metafile` or parse header XML comments starting with `wellmanifest:metafile:v1`."""
    },
    "application/zip": {
        "title": "application/zip (ZIP Archive)",
        "exts": [".zip"],
        "standard": "PKWARE APPNOTE / ISO/IEC 21320-1",
        "embedding": """### Embedding Strategies

1. **Standard `META-INF/metafile.json`**:
   Store the canonical metadata file inside the archive under `META-INF/metafile.json` or `.wellmanifest/metafile.json`.
2. **Archive Header Comment**:
   Store JSON string in the central directory End-of-Central-Directory (EOCD) archive comment field.""",
        "reading": """- Open ZIP with `zipfile`, read `META-INF/metafile.json` or `.wellmanifest/metafile.json`.
- Fall back to reading archive comment from EOCD."""
    },
    "application/epub+zip": {
        "title": "application/epub+zip (Electronic Publication)",
        "exts": [".epub"],
        "standard": "IDPF / W3C EPUB 3.3",
        "embedding": """### Embedding Strategies

1. **Package Document (`content.opf` / `<metadata>`)**:
   Add `<meta property="wm:docId">DOC-123</meta>` and `<link rel="wm:metafile" href="metafile.json"/>`.
2. **Container File (`META-INF/metafile.json`)**:
   Standard bundled sidecar within the EPUB OCF container.""",
        "reading": """- Inspect EPUB package OPF `<metadata>` section or extract `META-INF/metafile.json`."""
    },
    "application/vnd.openxmlformats": {
        "title": "Office Open XML (.docx, .xlsx, .pptx)",
        "exts": [".docx", ".xlsx", ".pptx"],
        "standard": "ISO/IEC 29500 / ECMA-376",
        "embedding": """### Embedding Strategies

1. **Custom Document Properties (`docProps/custom.xml`)**:
   Store properties in `<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/custom-properties">`:
   - Property `WellmanifestDocId` (vt:lpwstr)
   - Property `WellmanifestAmount` (vt:lpwstr)
   - Property `WellmanifestJSON` (vt:lpwstr - raw payload)
2. **Custom XML Data Storage Part (`customXml/item1.xml`)**:
   Attach canonical XML or JSON payload as an independent document part.""",
        "reading": """- Open zip archive of OOXML, parse `docProps/custom.xml` or custom XML part."""
    },
    "image/png": {
        "title": "image/png (Portable Network Graphics)",
        "exts": [".png"],
        "standard": "ISO/IEC 15948:2004 / W3C PNG Specification",
        "embedding": """### Embedding Strategies

1. **`iTXt` (International Textual Data Chunk)**:
   Keyword: `wellmanifest:metafile`
   Compression flag: `0` (uncompressed UTF-8) or `1` (deflate compressed).
   Text: complete JSON serialized payload.
2. **`tEXt` Chunk**:
   Keyword: `Wellmanifest`
   Text: JSON-serialized payload (Latin-1 encoded or Base64).
3. **`eXIf` Chunk**:
   Standard EXIF chunk containing UserComment.""",
        "reading": """- Parse PNG chunks before `IDAT`. When `iTXt` has keyword `wellmanifest:metafile`, extract and decode UTF-8 JSON.
- In Python Pillow: `image.text.get("wellmanifest:metafile")`."""
    },
    "image/jpeg": {
        "title": "image/jpeg (Joint Photographic Experts Group)",
        "exts": [".jpg", ".jpeg"],
        "standard": "ISO/IEC 10918-1 / JEITA CP-3451 (EXIF) / ISO 16684-1 (XMP)",
        "embedding": """### Embedding Strategies

1. **APP1 Marker - XMP Packet (`http://ns.adobe.com/xap/1.0/`)**:
   Embed RDF/XML containing namespace `https://wellmanifest.org/schemas/metafile/v1/`.
2. **APP1 Marker - EXIF `UserComment` (Tag 0x9286)**:
   Store UTF-8 JSON prefixed with `UNICODE` in tag 37510.
3. **APP2 / APP13 IPTC Photoshop Marker**:
   Store `Caption/Abstract` or custom record with `docId`.""",
        "reading": """- Scan APP1 segments for XMP URI or parse EXIF UserComment using Pillow / piexif."""
    },
    "image/webp": {
        "title": "image/webp (WebP Image Format)",
        "exts": [".webp"],
        "standard": "Google WebP Container Specification (RIFF)",
        "embedding": """### Embedding Strategies

1. **RIFF Chunk `XMP `**:
   Set `XMP` flag bit (0x04) in `VP8X` header chunk.
   Append chunk with FourCC `'XMP '` containing XMP packet with wellmanifest schema.
2. **RIFF Chunk `EXIF`**:
   Store standard EXIF buffer with UserComment.""",
        "reading": """- Read RIFF chunk list, parse `'XMP '` or `'EXIF'` chunk data."""
    },
    "image/svg+xml": {
        "title": "image/svg+xml (Scalable Vector Graphics)",
        "exts": [".svg"],
        "standard": "W3C SVG 1.1 / 2.0",
        "embedding": """### Embedding Strategies

1. **Standard `<metadata>` Element**:
   Inside `<svg>` root:
   ```xml
   <metadata id="wellmanifest-metafile">
     <wm:metafile xmlns:wm="https://wellmanifest.org/schemas/metafile/v1/">
       {"schema": "wellmanifest.metafile/v1", "docId": "DOC-123"}
     </wm:metafile>
   </metadata>
   ```
2. **`<script type="application/ld+json">` Block**.""",
        "reading": """- Parse XML, query `/svg/metadata` children or find element with ID `wellmanifest-metafile`."""
    },
    "image/tiff": {
        "title": "image/tiff (Tag Image File Format)",
        "exts": [".tiff", ".tif"],
        "standard": "TIFF 6.0 / Adobe TIFF Specification",
        "embedding": """### Embedding Strategies

1. **Tag 700 (0x02BC) - XMP Metadata**:
   Direct raw XML XMP packet containing wellmanifest namespace.
2. **Tag 37510 (0x9286) - UserComment (EXIF IFD)**:
   JSON payload.
3. **Tag 270 (0x010E) - ImageDescription**:
   Human readable title with `[wellmanifest docId=...]`.""",
        "reading": """- Read IFD entries for Tag 700 (XMP) or Tag 37510."""
    },
    "image/avif": {
        "title": "image/avif (AV1 Image File Format)",
        "exts": [".avif", ".heic"],
        "standard": "ISO/IEC 23000-22 (MIAF) / ISO/IEC 14496-12 (ISOBMFF)",
        "embedding": """### Embedding Strategies

1. **ISOBMFF `meta` Box**:
   Item of type `'mime'` with content type `application/json` or item of type `'Exif'` / `'XMP '`.""",
        "reading": """- Traverse ISOBMFF box hierarchy: `root -> meta -> iloc / idat`, extract item associated with MIME metadata."""
    },
    "image/gif": {
        "title": "image/gif (Graphics Interchange Format)",
        "exts": [".gif"],
        "standard": "CompuServe GIF89a",
        "embedding": """### Embedding Strategies

1. **Application Extension Block**:
   Application Identifier: `XMP Data` (8 bytes) + Auth Code: `XMP` (3 bytes).
   Contains complete XMP packet.
2. **Comment Extension Block (0xFE)**:
   Comment string: `wellmanifest:metafile:v1 <json>`.""",
        "reading": """- Scan GIF blocks for Extension Introducer `0x21` with label `0xFE` (Comment) or `0xFF` (Application)."""
    },
    "message/rfc822": {
        "title": "message/rfc822 (Email Message Format)",
        "exts": [".eml", ".msg"],
        "standard": "RFC 5322 / RFC 2045 (MIME)",
        "embedding": """### Embedding Strategies

1. **Custom `X-` Headers (RFC 5322)**:
   - `X-Wellmanifest-DocID`: `DOC-FV-3A0C5BB3A175D4A4`
   - `X-Wellmanifest-Type`: `faktura`
   - `X-Wellmanifest-Date`: `2026-09-07`
   - `X-Wellmanifest-Accounting`: `amount=250.00;currency=PLN;contractor=BOTERM`
   - `X-Wellmanifest-Payload-B64`: `<base64-encoded-json>`
2. **MIME Attachment**:
   Add a dedicated MIME sub-part of type `application/vnd.wellmanifest.metafile+json`.""",
        "reading": """- Parse headers via standard Python `email` module; read `X-Wellmanifest-*` headers."""
    },
    "text/plain": {
        "title": "text/plain (Plain Text)",
        "exts": [".txt"],
        "standard": "RFC 2046",
        "embedding": """### Embedding Strategies

1. **Leading Header Block**:
   ```text
   # --- WELLMANIFEST METAFILE v1 ---
   # docId: DOC-123
   # amount: 250.00
   # --- END METAFILE ---
   ```
2. **Trailing Envelope Block**:
   Placed at the end of the text file to preserve clean visual inspection.""",
        "reading": """- Match regex `(?s)# --- WELLMANIFEST METAFILE v1 ---\n(.*?)\n# --- END METAFILE ---`."""
    },
    "text/markdown": {
        "title": "text/markdown (Markdown Document)",
        "exts": [".md"],
        "standard": "CommonMark / GFM",
        "embedding": """### Embedding Strategies

1. **YAML Frontmatter (RFC / Jekyll / Hugo standard)**:
   ```markdown
   ---
   wellmanifest:
     schema: wellmanifest.metafile/v1
     docId: DOC-FV-3A0C5BB3A175D4A4
     accounting:
       amount: "250.00"
       currency: "PLN"
       contractor: "BOTERM"
   ---
   # Document content...
   ```
2. **HTML Comment**:
   `<!-- wellmanifest:metafile:v1 {"docId": "DOC-123"} -->`""",
        "reading": """- Extract YAML frontmatter block between initial `---` delimiters."""
    },
    "text/csv": {
        "title": "text/csv (Comma-Separated Values)",
        "exts": [".csv"],
        "standard": "RFC 4180",
        "embedding": """### Embedding Strategies

1. **Comment Header Lines (RFC 4180 extension)**:
   ```csv
   # wellmanifest:metafile:v1 {"docId": "BANK-2026.09", "type": "wyciag", "period": "2026.09"}
   Data;Kwota;Tytul;Nadawca
   2026-09-07;-250.00;Faktura 18054;BOTERM
   ```""",
        "reading": """- Read leading lines starting with `# wellmanifest:metafile:v1 `, parse remaining text as JSON."""
    },
    "text/html": {
        "title": "text/html (Hypertext Markup Language)",
        "exts": [".html", ".htm"],
        "standard": "W3C HTML5",
        "embedding": """### Embedding Strategies

1. **`<script type="application/ld+json" id="wellmanifest-metafile">`**:
   Clean, standard-compliant JSON-LD script tag in the `<head>` or `<body>`.
2. **`<meta name="wellmanifest:*" content="...">` Tags**:
   `<meta name="wellmanifest:docId" content="DOC-123">`""",
        "reading": """- Query `<script type="application/ld+json" id="wellmanifest-metafile">` or extract `<meta name="wellmanifest:...">`."""
    },
    "audio/mpeg": {
        "title": "audio/mpeg (MP3 Audio)",
        "exts": [".mp3"],
        "standard": "ISO/IEC 11172-3 / ID3v2.4",
        "embedding": """### Embedding Strategies

1. **ID3v2.4 User Defined Text Frame (`TXXX`)**:
   Description: `WELLMANIFEST_METAFILE`
   Value: JSON serialized payload.
2. **General Encapsulated Object (`GEOB`)**:
   MIME: `application/json`, Filename: `metafile.json`.""",
        "reading": """- Read ID3v2 tag, locate frame `TXXX` with description `WELLMANIFEST_METAFILE` or `GEOB`."""
    },
    "audio/flac": {
        "title": "audio/flac (Free Lossless Audio Codec)",
        "exts": [".flac"],
        "standard": "IETF FLAC Specification / Xiph.org Vorbis Comment",
        "embedding": """### Embedding Strategies

1. **Vorbis Comment Block**:
   Tag: `WELLMANIFEST_METAFILE=<JSON>`
   Tag: `WELLMANIFEST_DOCID=<docId>`""",
        "reading": """- Read FLAC `VORBIS_COMMENT` metadata block."""
    },
    "audio/wav": {
        "title": "audio/wav (Waveform Audio File Format)",
        "exts": [".wav"],
        "standard": "IBM/Microsoft RIFF / EBU BWF",
        "embedding": """### Embedding Strategies

1. **RIFF Chunk `id3 `**:
   Embedded ID3v2 tag with `TXXX:WELLMANIFEST_METAFILE`.
2. **RIFF `INFO` List Chunk**:
   `ISBJ` (Subject) set to `docId`, `ICMT` (Comment) set to JSON.""",
        "reading": """- Parse RIFF chunks for `'id3 '` or `'INFO'` sub-chunks."""
    },
    "audio/mp4": {
        "title": "audio/mp4 (M4A / AAC Audio)",
        "exts": [".m4a", ".aac"],
        "standard": "ISO/IEC 14496-14 (MP4)",
        "embedding": """### Embedding Strategies

1. **iTunes Metadata Atom (`moov.udta.meta.ilst`)**:
   Custom reverse-DNS atom `----:com.wellmanifest:metafile`.""",
        "reading": """- Traverse atoms down to `moov/udta/meta/ilst/----` with name `metafile` in domain `com.wellmanifest`."""
    },
    "video/mp4": {
        "title": "video/mp4 (MPEG-4 Part 14)",
        "exts": [".mp4"],
        "standard": "ISO/IEC 14496-14",
        "embedding": """### Embedding Strategies

1. **User Data Atom (`moov.udta`)**:
   Atom with type `WMET` (Wellmanifest Metadata) containing JSON string.
2. **Timed Metadata Track**:
   Dedicated metadata track for time-synchronized annotations.""",
        "reading": """- Search `moov.udta` for `WMET` or reverse-DNS metadata atom."""
    },
    "video/x-matroska": {
        "title": "video/x-matroska (Matroska / WebM Video)",
        "exts": [".mkv", ".webm"],
        "standard": "IETF RFC 8794 (EBML) / Matroska Specification",
        "embedding": """### Embedding Strategies

1. **Matroska `Tags` Element (0x1254C367)**:
   Add `SimpleTag` with `TagName: WELLMANIFEST_METAFILE` and `TagString: <json>`.
2. **Attached File (`Attachments` element)**:
   File name `metafile.json`, MIME `application/json`.""",
        "reading": """- Read Matroska EBML `Tags` master element or extract attachment `metafile.json`."""
    }
}

for mime, data in specs.items():
    p = base / mime / "README.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    content = f"""# {data["title"]}

- **Canonical MIME Type:** `{mime}`
- **File Extensions:** `{", ".join(data["exts"])}`
- **Applicable Standards:** {data["standard"]}

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `{mime}` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
{data["embedding"].strip()}

---

## 3. Reading Algorithm
{data["reading"].strip()}

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
"""
    p.write_text(content, encoding="utf-8")
    print(f"Generated {p}")
print("ALL SPECS GENERATED SUCCESSFULLY!")
