# text/tab-separated-values (TSV) Metafile Specification

## 1. Overview
- **MIME Type:** `text/tab-separated-values`
- **File Extensions:** `.tsv`
- **Standard:** IANA TSV / RFC 4180 variant

## 2. Embedding Mechanism
- In TSV tabular files, metadata is embedded as a leading `# wellmanifest:` comment line preceding the tabular data columns:
  ```tsv
  # wellmanifest:{"schema":"wellmanifest.metafile/v1","docId":"DOC-123","accounting":{"amount":"250.00","currency":"PLN"}}
  id	name	amount
  1	Item	250.00
  ```

## 3. Parsing Rules
1. Scan initial comment lines starting with `#`.
2. Extract the substring following `# wellmanifest:`.
3. Deserialize JSON string into the canonical `Metafile` object.
