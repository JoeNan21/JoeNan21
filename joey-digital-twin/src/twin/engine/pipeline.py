"""End-to-end reasoning pipeline.

  case -> retrieval -> evidence -> rules -> ranking -> red team -> confidence
       -> decision contract

Pure and deterministic: same inputs produce byte-identical output.
"""

from __future__ import annotations

from dataclasses import replace

from twin.engine import confidence as conf_mod
from twin.engine import reasoning, recommendation, red_team, rules
from twin.engine.modes import get_mode
from twin.engine.retrieval import retrieve
from twin.engine.signals import unknown_tags
from twin.memory.store import MemoryStore
from twin.providers.base import ProviderInfo
from twin.safety.readonly import assert_read_only
from twin.types import Case, Recommendation


class Pipeline:
    def __init__(self, store: MemoryStore | None = None) -> None:
        self.store = store or MemoryStore()

    def run(self, case: Case, provider_info: ProviderInfo) -> Recommendation:
        # Fail loudly if any external-write capability has been enabled.
        assert_read_only()

        mode = get_mode(case.mode)

        retrieval = retrieve(case, mode, self.store)
        enriched = replace(case, claims=case.claims + retrieval.claims)
        enriched = rules.inject_do_nothing(enriched) if mode.inject_do_nothing else enriched

        outcome = rules.apply_rules(enriched, mode)
        ranking = reasoning.rank(enriched, outcome)
        findings = red_team.run(enriched, mode, ranking)
        ranking, demotion = reasoning.apply_red_team(ranking, findings)

        live = [s for s in ranking if not s.gated_out]
        provisional = (
            "insufficient_evidence"
            if not live or (live[0].score <= 0 and live[0].kind.value != "do_nothing")
            else live[0].option_id
        )
        conf = conf_mod.compute(enriched, mode, findings, reasoning.margin(ranking), provisional)

        provenance = {
            **provider_info.as_dict(),
            "mode": mode.name,
            "authority": "READ_ONLY",
            "retrieved_memory_ids": list(retrieval.record_ids),
            "retrieval_reason": retrieval.reason,
            "skipped_superseded": list(retrieval.skipped_superseded),
            "excluded_synthetic_memory": list(retrieval.excluded_synthetic),
            "injected_options": [o.id for o in enriched.options if o.injected],
            "unrecognised_tags": unknown_tags({t for c in enriched.claims for t in c.tags}),
            "red_team_severity": red_team.severity_counts(findings),
            "score_margin": reasoning.margin(ranking),
        }
        return recommendation.build(
            enriched, mode, ranking, outcome, findings, conf, provenance, demotion
        )
