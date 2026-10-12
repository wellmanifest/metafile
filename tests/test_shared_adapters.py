"""Public-contract regression vectors for extracted adapter implementations."""
from contextlib import nullcontext
import json
import sys
from types import SimpleNamespace

import pytest
import yaml

from wellmanifest_metafile.core import Metafile
from wellmanifest_metafile.events import MetafileEvent
from wellmanifest_metafile import validator
from wellmanifest_metafile.adapters import data, image_extra, multimedia


@pytest.mark.parametrize("writer,loader,key", [
    (data.write_json_metafile, json.loads, "$metafile"),
    (data.write_yaml_metafile, yaml.safe_load, "_metafile"),
])
@pytest.mark.parametrize("initial", [None, "", '{"title": "Łódź", "nested": [1, 2]}', "[1, 2]", "{broken"])
def test_mapping_preserves_content_and_replaces_metadata(tmp_path, writer, loader, key, initial):
    path = tmp_path / "document"
    if initial is not None:
        path.write_text(initial, encoding="utf-8")
    meta = Metafile(docId="DOC-1", currency="PLN")
    writer(path, meta)
    decoded = loader(path.read_text(encoding="utf-8"))
    assert decoded[key] == meta.to_dict()
    if initial and "title" in initial:
        assert decoded["title"] == "Łódź"
        assert decoded["nested"] == [1, 2]
        assert "Łódź" in path.read_text(encoding="utf-8")
    else:
        assert set(decoded) == {key}
    writer(path, Metafile(docId="DOC-2"))
    assert loader(path.read_text(encoding="utf-8"))[key]["docId"] == "DOC-2"


@pytest.mark.parametrize("writer", [data.write_jsonl_metafile, data.write_csv_metafile])
@pytest.mark.parametrize("initial", [None, "", '# wellmanifest:old\na,b\n# wellmanifest:stale\n  # keep\nlast'])
def test_comment_header_replacement_preserves_records(tmp_path, writer, initial):
    path = tmp_path / "records"
    if initial is not None:
        path.write_text(initial, encoding="utf-8")
    meta = Metafile(docId="DOC-1")
    writer(path, meta)
    expected_records = "a,b\n  # keep\nlast" if initial else ""
    assert path.read_text(encoding="utf-8") == f"# wellmanifest:{meta.to_json(indent=None)}\n{expected_records}"
    writer(path, meta)
    assert path.read_text(encoding="utf-8").count("# wellmanifest:") == 1


@pytest.mark.parametrize("function,model,other", [
    (validator.validate_metafile, Metafile, MetafileEvent(event="staged", docId="DOC-1")),
    (validator.validate_event, MetafileEvent, Metafile(docId="DOC-1")),
])
@pytest.mark.parametrize("target", [None, [], "text", 42])
def test_invalid_validation_target_does_not_load_schema(monkeypatch, function, model, other, target):
    def unavailable():
        raise AssertionError("invalid targets must not load schemas")
    monkeypatch.setattr(validator, "get_metafile_schema", unavailable)
    monkeypatch.setattr(validator, "get_event_schema", unavailable)
    assert function(target) == (False, [f"Expected {model.__name__} or dict, got {type(target).__name__}"])
    assert function(other) == (False, [f"Expected {model.__name__} or dict, got {type(other).__name__}"])


@pytest.mark.parametrize("reader", [image_extra.read_tiff_metafile, image_extra.read_webp_metafile])
@pytest.mark.parametrize("tag,as_bytes", [(37510, False), (37510, True), (270, False), (270, True)])
def test_exif_contract_reads_both_tags_and_encodings(monkeypatch, tmp_path, reader, tag, as_bytes):
    meta = Metafile(docId="DOC-NATIVE")
    value = meta.to_json().encode("utf-8") if as_bytes else meta.to_json()
    image = SimpleNamespace(getexif=lambda: {tag: value})
    monkeypatch.setattr(image_extra.Image, "open", lambda path: nullcontext(image))
    assert reader(tmp_path / "image").to_dict() == meta.to_dict()


@pytest.mark.parametrize("reader", [image_extra.read_tiff_metafile, image_extra.read_webp_metafile])
def test_invalid_preferred_exif_uses_trailer_before_secondary_tag(monkeypatch, tmp_path, reader):
    path = tmp_path / "image"
    expected = Metafile(docId="DOC-TRAILER")
    path.write_bytes(b"image payload")
    image_extra._write_trailer_metafile(path, expected)
    image = SimpleNamespace(getexif=lambda: {37510: '{"docId":bad}', 270: Metafile(docId="DOC-SECONDARY").to_json()})
    monkeypatch.setattr(image_extra.Image, "open", lambda path: nullcontext(image))
    assert reader(path).to_dict() == expected.to_dict()


@pytest.mark.parametrize("module,name,reader,writer", [
    ("mutagen.flac", "FLAC", multimedia.read_flac_metafile, multimedia.write_flac_metafile),
    ("mutagen.oggvorbis", "OggVorbis", multimedia.read_ogg_metafile, multimedia.write_ogg_metafile),
])
@pytest.mark.parametrize("lowercase", [False, True])
def test_native_vorbis_tags_preserve_format_selection(monkeypatch, tmp_path, module, name, reader, writer, lowercase):
    path = tmp_path / "audio"
    path.write_bytes(b"native audio payload")
    meta = Metafile(docId="DOC-AUDIO")
    saves = []
    class Tags(dict):
        def save(self):
            saves.append(dict(self))
    key = multimedia.TAG_KEY.lower() if lowercase else multimedia.TAG_KEY
    tags = Tags({key: [meta.to_json()]})
    opened = []
    def native_type(actual_path):
        opened.append(actual_path)
        return tags
    monkeypatch.setitem(sys.modules, module, SimpleNamespace(**{name: native_type}))
    assert reader(path).to_dict() == meta.to_dict()
    writer(path, meta)
    assert opened == [path, path]
    assert saves == [dict(tags)]
    assert tags[multimedia.TAG_KEY] == meta.to_json()
    assert path.read_bytes() == b"native audio payload"


@pytest.mark.parametrize("module,name,reader,writer", [
    ("mutagen.flac", "FLAC", multimedia.read_flac_metafile, multimedia.write_flac_metafile),
    ("mutagen.oggvorbis", "OggVorbis", multimedia.read_ogg_metafile, multimedia.write_ogg_metafile),
])
@pytest.mark.parametrize("failure", ["missing_dependency", "invalid_audio", "save_failure"])
def test_audio_failure_keeps_payload_and_replaces_trailer(monkeypatch, tmp_path, module, name, reader, writer, failure):
    path = tmp_path / "audio"
    path.write_bytes(b"audio payload")
    old, new = Metafile(docId="DOC-OLD"), Metafile(docId="DOC-NEW")
    image_extra._write_trailer_metafile(path, old)
    class BrokenTags(dict):
        def save(self):
            raise ValueError("cannot save")
    def broken_type(path):
        if failure == "invalid_audio":
            raise ValueError("cannot decode")
        return BrokenTags()
    monkeypatch.setitem(sys.modules, module, None if failure == "missing_dependency" else SimpleNamespace(**{name: broken_type}))
    assert reader(path).to_dict() == old.to_dict()
    writer(path, new)
    assert reader(path).to_dict() == new.to_dict()
    assert path.read_bytes().startswith(b"audio payload")
    assert path.read_bytes().count(image_extra.TRAILER_PREFIX) == 1
