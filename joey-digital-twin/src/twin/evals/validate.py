"""Case validation, with contamination detection.

A badly authored case is worse than no case: it produces a number that looks
like evidence and is not. The expensive failure mode is hindsight - context
written with knowledge of how things turned out - because it is invisible in the
output and inflates agreement.

Errors block scoring. Warnings are judgement calls for the author.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from twin.engine.signals import unknown_tags
from twin.evals import loader

# Phrases that betray writing with knowledge of the outcome.
HINDSIGHT_MARKERS = (
    "turned out", "in hindsight", "with hindsight", "we later learned",
    "later learned", "as it happened", "this proved", "it proved",
    "eventually", "in the end", "ended up", "we now know", "looking back",
    "which was a mistake", "correctly", "wrongly", "should have",
)

# Phrases that state a decision rather than the information available before it.
DECISION_LEAK_MARKERS = (
    "we decided", "i decided", "we chose", "i chose", "we went with",
    "the decision was", "we opted", "we declined", "we accepted",
)

MIN_SUITE_SIZE = 25


@dataclass
class CaseReport:
    path: Path
    case_id: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value[:10], "%Y-%m-%d")
    except ValueError:
        return None


def _find_markers(text: str, markers: tuple[str, ...]) -> list[str]:
    lowered = text.lower()
    return [m for m in markers if re.search(rf"\b{re.escape(m)}\b", lowered)]


def validate_case(path: Path) -> CaseReport:  # noqa: C901 - a checklist, read top to bottom
    report = CaseReport(path=path)

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        report.errors.append(f"not valid JSON: {e}")
        return report
    if not isinstance(raw, dict):
        report.errors.append("case file must be a JSON object")
        return report
    report.case_id = str(raw.get("case_id", ""))

    # --- structural -------------------------------------------------------
    try:
        case = loader.load_case_for_inference(path)
    except Exception as e:  # noqa: BLE001 - surfacing any construction failure
        report.errors.append(f"cannot be loaded for inference: {type(e).__name__}: {e}")
        return report

    if not case.options:
        report.errors.append("no options; a case with no options cannot be decided")
    if not case.claims:
        report.errors.append("no claims; a case with no evidence cannot be reasoned about")
    if not case.as_of:
        report.errors.append("no as_of date; hindsight cannot be checked without it")

    option_ids = {o.id for o in case.options}
    claim_ids = {c.id for c in case.claims}

    for c in case.claims:
        for oid in (*c.supports_options, *c.opposes_options):
            if oid not in option_ids:
                report.errors.append(f"claim {c.id} references unknown option {oid!r}")
        for parent in c.derived_from:
            if parent not in claim_ids:
                report.warnings.append(
                    f"claim {c.id} derives from {parent!r}, which is not in this case"
                )
    for u in case.unknowns:
        for oid in u.blocks:
            if oid not in option_ids:
                report.errors.append(f"unknown {u.id} blocks unknown option {oid!r}")

    drift = unknown_tags({t for c in case.claims for t in c.tags})
    if drift:
        report.warnings.append(
            f"tags outside the controlled vocabulary: {drift} "
            "(fine if deliberate; they carry base weight and fire no rules)"
        )

    # --- hidden block -----------------------------------------------------
    try:
        answer = loader.load_case_answer(path)
    except loader.CaseFormatError as e:
        report.errors.append(str(e))
        return report

    if answer.actual_decision not in option_ids:
        report.errors.append(
            f"hidden.actual_decision {answer.actual_decision!r} is not one of the "
            f"options {sorted(option_ids)}; the case cannot be scored"
        )
    if not answer.actual_decision_kind:
        report.errors.append(
            "hidden.actual_decision_kind is required for material-agreement scoring"
        )
    for eid in answer.key_evidence_ids:
        if eid not in claim_ids:
            report.errors.append(f"hidden.key_evidence_ids references unknown claim {eid!r}")
    if not answer.reasoning_tags:
        report.warnings.append(
            "hidden.reasoning_tags is empty; reasoning similarity will score 0 "
            "even when the Twin reasons correctly"
        )
    if not answer.expected_red_team:
        report.warnings.append(
            "hidden.expected_red_team is empty; red-team recall is unmeasured for this case"
        )

    # --- contamination ----------------------------------------------------
    context_text = json.dumps({k: v for k, v in raw.items() if k != loader.HIDDEN_KEY})

    for marker in _find_markers(context_text, HINDSIGHT_MARKERS):
        report.errors.append(
            f"hindsight marker {marker!r} in the context block; context must contain "
            "only what was known at decision time"
        )
    for marker in _find_markers(context_text, DECISION_LEAK_MARKERS):
        report.errors.append(
            f"decision-leak marker {marker!r} in the context block; the decision "
            "belongs in the hidden block only"
        )

    for oid in option_ids:
        if re.search(rf"\b{re.escape(oid)}\b", case.question):
            report.warnings.append(
                f"question names option {oid!r}; check it does not signal the answer"
            )

    if answer.outcome:
        outcome_words = {w for w in re.findall(r"\w{6,}", answer.outcome.lower())}
        leaked = outcome_words & {w for w in re.findall(r"\w{6,}", context_text.lower())}
        distinctive = leaked - {"synthetic", "outcome", "exists"}
        if len(distinctive) >= 5:
            report.warnings.append(
                f"context shares {len(distinctive)} distinctive words with hidden.outcome; "
                "check the outcome has not been written back into the context"
            )

    # --- hindsight by date ------------------------------------------------
    as_of = _parse_date(case.as_of)
    if as_of:
        for c in case.claims:
            claim_date = _parse_date(c.date)
            if claim_date and claim_date > as_of:
                report.errors.append(
                    f"claim {c.id} is dated {c.date}, after as_of {case.as_of}; "
                    "it was not available at decision time"
                )

    return report


@dataclass
class SuiteReport:
    cases: list[CaseReport]
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.cases) and bool(self.cases)

    @property
    def error_count(self) -> int:
        return sum(len(c.errors) for c in self.cases)


def validate_suite(root: Path) -> SuiteReport:
    paths = loader.discover(root)
    reports = [validate_case(p) for p in paths]
    suite = SuiteReport(cases=reports)

    if not paths:
        suite.warnings.append(f"no case files found in {root}")
        return suite

    ids = [r.case_id for r in reports if r.case_id]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        suite.warnings.append(f"duplicate case_id values: {duplicates}")

    kinds: list[str] = []
    modes: list[str] = []
    for path in paths:
        try:
            kinds.append(loader.load_case_answer(path).actual_decision_kind)
            modes.append(json.loads(path.read_text(encoding="utf-8")).get("mode", "general"))
        except Exception:  # noqa: BLE001 - per-case errors already reported above
            continue

    if len(paths) < MIN_SUITE_SIZE:
        suite.warnings.append(
            f"{len(paths)} cases; {MIN_SUITE_SIZE}+ are needed before an agreement "
            "rate is worth quoting (docs/evaluation-methodology.md)"
        )
    if kinds and len(set(kinds)) == 1:
        suite.warnings.append(
            f"every case resolves to kind {kinds[0]!r}; a suite with no variance "
            "cannot distinguish judgement from a constant answer"
        )
    conservative = {"do_nothing", "decline", "exit"}
    if kinds and not (set(kinds) & conservative):
        suite.warnings.append(
            "no case where the decision was to decline or do nothing; a suite of "
            "only action decisions teaches that action is always correct"
        )
    if modes and len(set(modes)) == 1 and len(paths) >= MIN_SUITE_SIZE:
        suite.warnings.append(f"every case is mode {modes[0]!r}; results will not generalise")

    return suite


def render(suite: SuiteReport) -> str:
    lines: list[str] = []
    for report in suite.cases:
        status = "OK  " if report.ok else "FAIL"
        lines.append(f"{status} {report.path.name} ({report.case_id or 'no case_id'})")
        lines.extend(f"       ERROR   {e}" for e in report.errors)
        lines.extend(f"       warning {w}" for w in report.warnings)
    if suite.warnings:
        lines.append("")
        lines.append("SUITE")
        lines.extend(f"       warning {w}" for w in suite.warnings)
    lines.append("")
    passed = sum(1 for c in suite.cases if c.ok)
    lines.append(f"{passed}/{len(suite.cases)} cases valid; {suite.error_count} errors")
    return "\n".join(lines)
