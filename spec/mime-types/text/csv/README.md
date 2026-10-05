# text/csv (Comma-Separated Values)

- **Canonical MIME Type:** `text/csv`
- **File Extensions:** `.csv`
- **Applicable Standards:** RFC 4180

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `text/csv` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **Comment Header Lines (RFC 4180 extension)**:
   ```csv
   # wellmanifest:metafile:v1 {"docId": "BANK-2026.09", "type": "wyciag", "period": "2026.09"}
   Data;Kwota;Tytul;Nadawca
   2026-09-07;-250.00;Faktura 18054;BOTERM
   ```

---

## 3. Reading Algorithm
- Read leading lines starting with `# wellmanifest:metafile:v1 `, parse remaining text as JSON.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
