"""Memory schema, provenance, supersession and contradiction handling."""

from __future__ import annotations

import json

import pytest

from twin.memory.schema import MemoryRecord, SchemaError
from twin.memory.store import MemoryStore


def _rec(**kw) -> MemoryRecord:
    base = dict(id="r1", type="COMPANY", label="X", grade="FACT", source="s",
                provenance="seed:test", recorded_at="2026-01-01")
    base.update(kw)
    return MemoryRecord(**base)  # type: ignore[arg-type]


def test_valid_record_passes():
    _rec().validate()


def test_unknown_record_type_is_rejected():
    with pytest.raises(SchemaError, match="unknown record type"):
        _rec(type="VIBE").validate()


@pytest.mark.parametrize("field", ["id", "provenance", "recorded_at"])
def test_required_fields_are_enforced(field):
    with pytest.raises(SchemaError, match="missing required field"):
        _rec(**{field: ""}).validate()


def test_fact_record_requires_a_source():
    with pytest.raises(SchemaError, match="FACT record requires a source"):
        _rec(source=None).validate()


def test_confidence_bounds_are_enforced():
    with pytest.raises(SchemaError, match="confidence"):
        _rec(confidence=2.0).validate()


def test_polarity_is_validated():
    with pytest.raises(SchemaError, match="polarity"):
        _rec(polarity=0).validate()


def test_record_cannot_supersede_itself():
    with pytest.raises(SchemaError, match="cannot supersede itself"):
        _rec(superseded_by="r1").validate()


def test_unknown_fields_are_rejected_so_schema_drift_is_visible():
    with pytest.raises(SchemaError, match="unknown fields"):
        MemoryRecord.from_dict({"id": "r", "type": "COMPANY", "vibes": "high"})


def test_superseded_records_are_excluded_from_active_but_not_deleted(memory_root):
    store = MemoryStore.load(memory_root)
    superseded = [r for r in store.records if not r.active]
    assert superseded, "fixture has no superseded record; test would pass vacuously"
    for r in superseded:
        assert store.by_id(r.id) is not None, "superseded record was deleted"
        assert r not in store.active()


def test_newer_does_not_win_automatically_supersession_must_be_explicit(memory_root):
    """A newer record with no supersedes link does not displace an older one."""
    store = MemoryStore.load(memory_root)
    old = _rec(id="old", recorded_at="2020-01-01")
    new = _rec(id="new", recorded_at="2026-01-01")
    both = MemoryStore([old, new])
    assert len(both.active()) == 2
    assert store.by_id("lesson-profile-events-old").superseded_by == "lesson-profile-events-current"


def test_contradictions_are_reported_not_resolved(memory_root):
    store = MemoryStore.load(memory_root)
    pairs = store.contradiction_pairs()
    assert pairs, "fixture has no contradiction; test would pass vacuously"
    for a, b in pairs:
        assert store.by_id(a) is not None and store.by_id(b) is not None


def test_every_record_in_the_repository_validates(memory_root):
    store = MemoryStore.load(memory_root)
    for r in store.records:
        r.validate()


def test_all_repository_memory_is_labelled_synthetic(memory_root):
    """AGENTS.md section 5: no real data about Joey may be committed."""
    for r in MemoryStore.load(memory_root).records:
        assert r.synthetic is True, f"{r.id} is not labelled synthetic"


def test_every_record_carries_provenance(memory_root):
    for r in MemoryStore.load(memory_root).records:
        assert r.provenance, f"{r.id} has no provenance; its origin is untraceable"


def test_store_loads_both_object_and_array_files(tmp_path):
    (tmp_path / "one.json").write_text(json.dumps(
        {"id": "a", "type": "PERSON", "grade": "ASSUMPTION",
         "provenance": "p", "recorded_at": "2026-01-01"}), encoding="utf-8")
    (tmp_path / "many.json").write_text(json.dumps(
        [{"id": "b", "type": "PERSON", "grade": "ASSUMPTION",
          "provenance": "p", "recorded_at": "2026-01-01"}]), encoding="utf-8")
    assert len(MemoryStore.load(tmp_path)) == 2


def test_missing_memory_root_yields_an_empty_store(tmp_path):
    assert len(MemoryStore.load(tmp_path / "nope")) == 0
