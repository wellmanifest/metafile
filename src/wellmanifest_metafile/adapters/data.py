"""Adapters for structured data formats: JSON, JSONL, XML, CSV, TSV, YAML, HTML."""
from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET

import yaml

from ..core import Metafile


# ---------------- JSON & JSONL ----------------
def read_json_metafile(file_path: Path | str) -> Optional[Metafile]:
    path = Path(file_path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            if "$metafile" in data:
                return Metafile.from_dict(data["$metafile"])
            if "metafile" in data:
                return Metafile.from_dict(data["metafile"])
            if "schema" in data and str(data["schema"]).startswith("wellmanifest.metafile"):
                return Metafile.from_dict(data)
    except Exception:
        pass
    return None


def write_json_metafile(file_path: Path | str, meta: Metafile) -> None:
    path = Path(file_path)
    data = {}
    if path.is_file() and path.stat().st_size > 0:
        try:
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    data = loaded
        except Exception:
            data = {}
    data["$metafile"] = meta.to_dict()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def read_jsonl_metafile(file_path: Path | str) -> Optional[Metafile]:
    path = Path(file_path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("# wellmanifest:"):
                    raw = line.split("# wellmanifest:", 1)[1].strip()
                    return Metafile.from_json(raw)
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        if "$metafile" in obj:
                            return Metafile.from_dict(obj["$metafile"])
                        if "_metafile" in obj:
                            return Metafile.from_dict(obj["_metafile"])
                        if "schema" in obj and str(obj["schema"]).startswith("wellmanifest.metafile"):
                            return Metafile.from_dict(obj)
                except Exception:
                    continue
    except Exception:
        pass
    return None


def write_jsonl_metafile(file_path: Path | str, meta: Metafile) -> None:
    path = Path(file_path)
    lines = []
    if path.is_file():
        with open(path, "r", encoding="utf-8") as f:
            lines = [l for l in f if not l.startswith("# wellmanifest:")]
    header = f"# wellmanifest:{meta.to_json(indent=None)}\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(header)
        f.writelines(lines)


# ---------------- CSV & TSV ----------------
def read_csv_metafile(file_path: Path | str) -> Optional[Metafile]:
    path = Path(file_path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# wellmanifest:"):
                    raw = line.split("# wellmanifest:", 1)[1].strip()
                    return Metafile.from_json(raw)
    except Exception:
        pass
    return None


def write_csv_metafile(file_path: Path | str, meta: Metafile) -> None:
    path = Path(file_path)
    lines = []
    if path.is_file():
        with open(path, "r", encoding="utf-8") as f:
            lines = [l for l in f if not l.startswith("# wellmanifest:")]
    header = f"# wellmanifest:{meta.to_json(indent=None)}\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(header)
        f.writelines(lines)


# ---------------- XML & SVG ----------------
def read_xml_metafile(file_path: Path | str) -> Optional[Metafile]:
    path = Path(file_path)
    try:
        content = path.read_text(encoding="utf-8")
        # Match <metadata id="wellmanifest-metafile"> ... </metadata> or wm:metafile
        m = re.search(r'<metadata[^>]*id=["\']wellmanifest-metafile["\'][^>]*>(.*?)</metadata>', content, re.DOTALL | re.IGNORECASE)
        if m:
            raw = m.group(1).strip()
            # strip CDATA if present
            raw = re.sub(r'^\s*<!\[CDATA\[(.*)\]\]>\s*$', r'\1', raw, flags=re.DOTALL)
            return Metafile.from_json(raw.strip())
        # Try processing instruction <?wellmanifest-metafile json="..."?>
        m2 = re.search(r'<\?wellmanifest-metafile\s+(.*?)\?>', content, re.DOTALL)
        if m2:
            return Metafile.from_json(m2.group(1).strip())
    except Exception:
        pass
    return None


def write_xml_metafile(file_path: Path | str, meta: Metafile) -> None:
    path = Path(file_path)
    content = ""
    if path.is_file():
        content = path.read_text(encoding="utf-8")

    meta_tag = f'<metadata id="wellmanifest-metafile"><![CDATA[{meta.to_json()}]]></metadata>'
    # Replace existing or insert
    if re.search(r'<metadata[^>]*id=["\']wellmanifest-metafile["\'][^>]*>.*?</metadata>', content, re.DOTALL | re.IGNORECASE):
        new_content = re.sub(r'<metadata[^>]*id=["\']wellmanifest-metafile["\'][^>]*>.*?</metadata>', meta_tag, content, flags=re.DOTALL | re.IGNORECASE)
    elif "<svg" in content:
        new_content = re.sub(r'(<svg[^>]*>)', r'\1\n  ' + meta_tag, content, count=1)
    elif "</" in content:
        # insert before root closing tag
        idx = content.rfind("</")
        new_content = content[:idx] + f"  {meta_tag}\n" + content[idx:]
    else:
        new_content = f'<?xml version="1.0" encoding="utf-8"?>\n<root>\n  {meta_tag}\n</root>\n'
    path.write_text(new_content, encoding="utf-8")


# ---------------- YAML ----------------
def read_yaml_metafile(file_path: Path | str) -> Optional[Metafile]:
    path = Path(file_path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            if "_metafile" in data:
                return Metafile.from_dict(data["_metafile"])
            if "schema" in data and str(data["schema"]).startswith("wellmanifest.metafile"):
                return Metafile.from_dict(data)
    except Exception:
        pass
    return None


def write_yaml_metafile(file_path: Path | str, meta: Metafile) -> None:
    path = Path(file_path)
    data = {}
    if path.is_file() and path.stat().st_size > 0:
        try:
            with open(path, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
                if isinstance(loaded, dict):
                    data = loaded
        except Exception:
            data = {}
    data["_metafile"] = meta.to_dict()
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


# ---------------- HTML ----------------
def read_html_metafile(file_path: Path | str) -> Optional[Metafile]:
    path = Path(file_path)
    try:
        content = path.read_text(encoding="utf-8")
        m = re.search(r'<script[^>]*id=["\']wellmanifest-metafile["\'][^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
        if m:
            return Metafile.from_json(m.group(1).strip())
    except Exception:
        pass
    return None


def write_html_metafile(file_path: Path | str, meta: Metafile) -> None:
    path = Path(file_path)
    content = ""
    if path.is_file():
        content = path.read_text(encoding="utf-8")

    tag = f'<script type="application/ld+json" id="wellmanifest-metafile">\n{meta.to_json()}\n</script>'
    if re.search(r'<script[^>]*id=["\']wellmanifest-metafile["\'][^>]*>.*?</script>', content, re.DOTALL | re.IGNORECASE):
        new_content = re.sub(r'<script[^>]*id=["\']wellmanifest-metafile["\'][^>]*>.*?</script>', tag, content, flags=re.DOTALL | re.IGNORECASE)
    elif "<head>" in content:
        new_content = content.replace("<head>", f"<head>\n  {tag}\n", 1)
    elif "<body>" in content:
        new_content = content.replace("<body>", f"<body>\n  {tag}\n", 1)
    else:
        new_content = f"<!DOCTYPE html>\n<html>\n<head>\n{tag}\n</head>\n<body>\n{content}\n</body>\n</html>"
    path.write_text(new_content, encoding="utf-8")
