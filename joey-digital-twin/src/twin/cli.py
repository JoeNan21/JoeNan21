"""twin - CLI for the Joey Digital Twin decision engine.

Deliberately a CLI. AGENTS.md section 2: the engine matters more than the UI, and
a UI would consume effort that has not yet been earned by evidence.

Commands:
  twin decide --mode career case.json
  twin eval --suite evals/historical_decisions
  twin validate evals/historical_decisions [--baseline]
  twin modes
  twin memory
  twin safety
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

from twin import __version__
from twin.engine.modes import MODES, UnknownModeError, available_modes
from twin.evals import harness, loader, report, validate
from twin.memory.store import MemoryStore
from twin.providers import registry
from twin.providers.base import ProviderUnavailable
from twin.safety.readonly import CAPABILITIES, assert_read_only
from twin.types import Recommendation

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MEMORY = ROOT / "memory"
DEFAULT_SUITE = ROOT / "evals" / "historical_decisions"


def _render(rec: Recommendation) -> str:
    o = []
    o.append("=" * 72)
    o.append(f"DECISION        : {rec.decision_label}  [{rec.decision}]")
    o.append(f"KIND            : {rec.decision_kind}")
    o.append(f"MODE            : {rec.mode}")
    o.append(f"CONFIDENCE      : {rec.confidence:.2f} ({rec.confidence_band})")
    if rec.confidence_ceiling_applied:
        o.append(f"  ceiling applied: {rec.confidence_ceiling_applied}")
    o.append("=" * 72)
    o.append("")
    o.append("WHY")
    o.append(f"  {rec.why}")
    o.append("")

    def block(title: str, items: list[str]) -> None:
        o.append(title)
        if items:
            o.extend(f"  - {i}" for i in items)
        else:
            o.append("  (none)")
        o.append("")

    block("FACTS", rec.facts)
    block("INFERENCES", rec.inferences)
    block("ASSUMPTIONS", rec.assumptions)
    block("UNKNOWN INFORMATION", rec.unknowns)
    block("CONTRADICTIONS", rec.contradictions)

    o.append("COUNTERARGUMENT")
    o.append(f"  {rec.counterargument}")
    o.append("")
    o.append("RED-TEAM VIEW")
    if rec.red_team:
        for f in rec.red_team:
            o.append(f"  [{f['severity'].upper():<6}] {f['challenge']}")
            o.append(f"           {f['finding']}")
    else:
        o.append("  (no findings triggered)")
    o.append("")
    block("WHAT MUST BE TRUE", rec.what_must_be_true)
    block("WHAT WOULD CHANGE MY MIND", rec.what_would_change_my_mind)

    o.append("OPTION RANKING")
    for r in rec.option_ranking:
        flag = " GATED" if r["gated_out"] else ""
        o.append(f"  {r['score']:>8.3f}  {r['option_id']:<24} [{r['kind']}]{flag}")
        for reason in r["gate_reasons"]:
            o.append(f"            ! {reason}")
    o.append("")
    o.append("RECOMMENDED NEXT ACTION")
    o.append(f"  {rec.recommended_next_action}")
    o.append("")
    o.append("-" * 72)
    o.append("v0.1 is READ-ONLY. This is a recommendation. Joey decides and acts.")
    return "\n".join(o)


def cmd_decide(args: argparse.Namespace) -> int:
    case_path = Path(args.case)
    if not case_path.exists():
        print(f"error: case file not found: {case_path}", file=sys.stderr)
        return 2
    case = loader.load_case_for_inference(case_path)
    if args.mode:
        case = replace(case, mode=args.mode)
    try:
        provider = registry.build(
            args.provider, memory_root=Path(args.memory), model=args.model,
            allow_network=args.allow_network,
        )
        rec = provider.decide(case)
    except UnknownModeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except ProviderUnavailable as e:
        print(f"provider unavailable: {e}", file=sys.stderr)
        return 3
    print(rec.to_json() if args.json else _render(rec))
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    suite = Path(args.suite)
    provider = registry.build(args.provider, memory_root=Path(args.memory))
    result, _ = harness.run_suite(suite, provider)
    baseline = None
    if args.baseline:
        baseline_result, _ = harness.run_suite(suite, registry.build("baseline_naive"))
        baseline = baseline_result
    if args.json:
        payload = {"result": result.to_dict()}
        if baseline:
            payload["baseline"] = baseline.to_dict()
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(report.render(result, baseline))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Check cases for structural validity and evaluation contamination."""
    target = Path(args.target)
    if target.is_dir():
        suite = validate.validate_suite(target)
    elif target.is_file():
        suite = validate.SuiteReport(cases=[validate.validate_case(target)])
    else:
        print(f"error: no such file or directory: {target}", file=sys.stderr)
        return 2
    print(validate.render(suite))
    return 0 if suite.ok else 1


def cmd_modes(_: argparse.Namespace) -> int:
    for name in available_modes():
        m = MODES[name]
        print(f"{name:<10} commercial={str(m.commercial):<5} "
              f"personal_memory={str(m.use_personal_memory):<5} "
              f"required={list(m.required_signals)}")
    return 0


def cmd_memory(args: argparse.Namespace) -> int:
    store = MemoryStore.load(Path(args.memory))
    print(f"{len(store)} records ({len(store.active())} active)")
    for r in store.records:
        state = "" if r.active else "  [SUPERSEDED]"
        print(f"  {r.id:<28} {r.type:<12} grade={r.grade:<10} "
              f"conf={r.confidence:.2f} synthetic={r.synthetic}{state}")
    pairs = store.contradiction_pairs()
    if pairs:
        print("contradictions:")
        for a, b in pairs:
            print(f"  {a} <-> {b}")
    return 0


def cmd_safety(_: argparse.Namespace) -> int:
    assert_read_only()
    print("authority: READ_ONLY (v0.1)")
    print("external-write capabilities (all must be False):")
    for k, v in sorted(CAPABILITIES.items()):
        print(f"  {k:<24} {v}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="twin", description="Joey Digital Twin (read-only, v0.1)")
    p.add_argument("--version", action="version", version=f"twin {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("decide", help="produce a recommendation for a case file")
    d.add_argument("case")
    d.add_argument("--mode", default=None, choices=available_modes())
    d.add_argument("--provider", default=registry.DEFAULT_PROVIDER, choices=list(registry.NAMES))
    d.add_argument("--model", default=None)
    d.add_argument("--memory", default=str(DEFAULT_MEMORY))
    d.add_argument("--allow-network", action="store_true",
                   help="permit an LLM provider to use the network (never a write)")
    d.add_argument("--json", action="store_true")
    d.set_defaults(func=cmd_decide)

    e = sub.add_parser("eval", help="run the historical decision evaluation suite")
    e.add_argument("--suite", default=str(DEFAULT_SUITE))
    e.add_argument("--provider", default=registry.DEFAULT_PROVIDER, choices=list(registry.NAMES))
    e.add_argument("--memory", default=str(DEFAULT_MEMORY))
    e.add_argument("--baseline", action="store_true", help="also run the naive baseline")
    e.add_argument("--json", action="store_true")
    e.set_defaults(func=cmd_eval)

    v = sub.add_parser("validate", help="check cases for validity and contamination")
    v.add_argument("target", nargs="?", default=str(DEFAULT_SUITE),
                   help="a case file or a suite directory")
    v.set_defaults(func=cmd_validate)

    m = sub.add_parser("modes", help="list decision modes")
    m.set_defaults(func=cmd_modes)

    mem = sub.add_parser("memory", help="inspect the memory store")
    mem.add_argument("--memory", default=str(DEFAULT_MEMORY))
    mem.set_defaults(func=cmd_memory)

    s = sub.add_parser("safety", help="show the v0.1 read-only capability gate")
    s.set_defaults(func=cmd_safety)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
