"""CLI surface. The interface is deliberately small; it must still be correct."""

from __future__ import annotations

import json

import pytest

from twin import cli


def test_decide_renders_the_full_contract(capsys, suite_root):
    path = next(suite_root.glob("SYN-001*.json"))
    assert cli.main(["decide", str(path)]) == 0
    out = capsys.readouterr().out
    for heading in ("DECISION", "WHY", "FACTS", "ASSUMPTIONS", "UNKNOWN INFORMATION",
                    "COUNTERARGUMENT", "RED-TEAM VIEW", "CONFIDENCE",
                    "WHAT WOULD CHANGE MY MIND", "RECOMMENDED NEXT ACTION"):
        assert heading in out


def test_decide_always_states_the_read_only_boundary(capsys, suite_root):
    cli.main(["decide", str(next(suite_root.glob("SYN-002*.json")))])
    assert "READ-ONLY" in capsys.readouterr().out


def test_decide_json_output_is_valid(capsys, suite_root):
    cli.main(["decide", str(next(suite_root.glob("SYN-002*.json"))), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["case_id"] == "SYN-002"
    assert payload["decision"]


def test_decide_accepts_a_mode_override(capsys, suite_root):
    cli.main(["decide", str(next(suite_root.glob("SYN-001*.json"))),
              "--mode", "general", "--json"])
    assert json.loads(capsys.readouterr().out)["mode"] == "general"


def test_decide_rejects_an_unknown_mode(suite_root):
    with pytest.raises(SystemExit):
        cli.main(["decide", str(next(suite_root.glob("SYN-001*.json"))), "--mode", "vibes"])


def test_missing_case_file_exits_non_zero(capsys):
    assert cli.main(["decide", "/nonexistent/case.json"]) == 2


def test_llm_provider_without_credentials_exits_cleanly(capsys, suite_root, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    code = cli.main(["decide", str(next(suite_root.glob("SYN-001*.json"))),
                     "--provider", "anthropic"])
    assert code == 3
    assert "provider unavailable" in capsys.readouterr().err


def test_eval_reports_the_agreement_rate(capsys):
    assert cli.main(["eval"]) == 0
    assert "Decision Agreement Rate" in capsys.readouterr().out


def test_eval_with_baseline_reports_both(capsys):
    cli.main(["eval", "--baseline"])
    out = capsys.readouterr().out
    assert "BASELINE COMPARISON" in out and "baseline_naive" in out


def test_eval_json_carries_both_results(capsys):
    cli.main(["eval", "--baseline", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert "result" in payload and "baseline" in payload


def test_safety_command_lists_every_capability_as_false(capsys):
    assert cli.main(["safety"]) == 0
    out = capsys.readouterr().out
    assert "READ_ONLY" in out and "True" not in out


def test_modes_command_lists_all_modes(capsys):
    cli.main(["modes"])
    out = capsys.readouterr().out
    for m in ("sales", "career", "sorrento", "caos", "general"):
        assert m in out


def test_memory_command_reports_superseded_records(capsys):
    cli.main(["memory"])
    assert "SUPERSEDED" in capsys.readouterr().out


def test_validate_command_passes_on_the_committed_suite(capsys):
    assert cli.main(["validate"]) == 0
    assert "cases valid" in capsys.readouterr().out


def test_validate_command_exits_non_zero_on_a_bad_case(capsys, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"case_id": "X", "question": "?"}', encoding="utf-8")
    assert cli.main(["validate", str(bad)]) == 1
    assert "ERROR" in capsys.readouterr().out


def test_validate_command_reports_a_missing_target(capsys):
    assert cli.main(["validate", "/nonexistent/path"]) == 2
    assert "no such file" in capsys.readouterr().err
