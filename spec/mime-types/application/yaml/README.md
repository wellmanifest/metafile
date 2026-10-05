# application/yaml (YAML) Metafile Specification

## 1. Overview
- **MIME Type:** `application/yaml` (also `text/yaml`)
- **File Extensions:** `.yaml`, `.yml`
- **Standard:** YAML 1.2

## 2. Embedding Mechanism
- In native YAML files, metadata is stored as a top-level `_metafile` key or embedded frontmatter:
  ```yaml
  _metafile:
    schema: "wellmanifest.metafile/v1"
    docId: "DOC-YAML-001"
    accounting:
      amount: "500.00"
      currency: "PLN"
      contractor: "SUPPLIER"
    location:
      country: "PL"
      city: "Gdańsk"
  
  # Original payload
  app:
    name: "Service"
    port: 8080
  ```

## 3. Parsing Rules
1. Load document using safe YAML deserializer.
2. If `_metafile` key is present, instantiate `Metafile.from_dict(data["_metafile"])`.
3. If document root contains `"schema": "wellmanifest.metafile/v1"`, parse root dictionary directly.
