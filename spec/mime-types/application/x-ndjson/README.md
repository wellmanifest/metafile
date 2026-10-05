# application/x-ndjson (JSONL) Metafile Specification

## 1. Overview
- **MIME Type:** `application/x-ndjson`
- **File Extensions:** `.jsonl`, `.ndjson`
- **Standard:** Newline Delimited JSON

## 2. Embedding Mechanism
- In JSONL files, metadata is embedded as a single-line comment header at the top of the file:
  ```jsonl
  # wellmanifest:{"schema":"wellmanifest.metafile/v1","docId":"DOC-123","accounting":{"amount":"100.00","currency":"PLN"}}
  {"record": 1, "data": "value"}
  {"record": 2, "data": "value"}
  ```
- Alternatively, if records are uniform JSON objects, a root metadata record `{"_metafile": {...}}` or `{"schema": "wellmanifest.metafile/v1", ...}` can be placed as the first record line.

## 3. Parsing Rules
1. Check line 1 for `# wellmanifest:`. If present, parse the remaining substring as JSON.
2. Otherwise, check if the first JSON object contains `"$metafile"`, `"_metafile"`, or `"schema": "wellmanifest.metafile/v1"`.
