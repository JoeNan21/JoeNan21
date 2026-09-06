"""Evidence classification, weighting, contradiction detection.

Implements cognition/evidence-policy.md.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime

from twin.engine import signals
from twin.types import Claim, EvidencePromotionError, Grade


def promote(claim: Claim, new_grade: Grade) -> Claim:
    """Change a claim's grade.

    Promotion toward FACT is forbidden: it is how inference silently becomes
    fact. Downgrades are permitted because they are conservative.
    """
    order = {Grade.UNKNOWN: 0, Grade.ASSUMPTION: 1, Grade.INFERENCE: 2, Grade.FACT: 3}
    if order[new_grade] > order[claim.grade]:
        raise EvidencePromotionError(
            f"claim {claim.id!r}: refusing to promote {claim.grade.value} -> "
            f"{new_grade.value}. New sourced input is a new claim, not a mutation."
        )
    return replace(claim, grade=new_grade)


def _parse(d: str | None) -> date | None:
    if not d:
        return None
    try:
        return datetime.strptime(d[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def temporal_factor(claim: Claim, as_of: str | None) -> float:
    """Age discount for volatile signals only.

    Durable claims do not decay. Newness is never a bonus: newer does not mean
    correct (cognition/evidence-policy.md).
    """
    if not any(signals.is_volatile(t) for t in claim.tags):
        return 1.0
    claim_date, ref = _parse(claim.date), _parse(as_of)
    if claim_date is None or ref is None:
        return 0.9  # undated volatile claim: mild discount, not a free pass
    months = max(0.0, (ref - claim_date).days / 30.44)
    if months <= 3:
        return 1.0
    if months <= 12:
        return 0.85
    if months <= 24:
        return 0.65
    return 0.45


def effective_weight(claim: Claim, as_of: str | None, tag_weights: dict[str, float]) -> float:
    """Claim weight after grade, reliability, relevance, mode weighting and age."""
    mode_factor = 1.0
    if claim.tags:
        mode_factor = max(tag_weights.get(t, 1.0) for t in claim.tags)
    return claim.weight * mode_factor * temporal_factor(claim, as_of)


def find_contradictions(claims: tuple[Claim, ...]) -> list[tuple[str, str, str]]:
    """Detect contradicting claim pairs.

    Two claims contradict when either:
      * names the other in `contradicts` (always authoritative), or
      * shares a tag with opposing polarity AND bears on the same option from
        opposite sides.

    The second condition is deliberately narrow. An earlier version fired on any
    shared tag with differing polarity, which flagged retrieved context records
    (a COMPANY entity tagged `approval_chain`) as contradicting case evidence.
    A contradiction is evidence pulling one option two ways, not two claims that
    happen to mention the same subject.

    Both claims are retained; neither is silently trusted.
    Returns (claim_a, claim_b, reason).
    """
    out: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()
    by_id = {c.id: c for c in claims}

    for claim in claims:
        for other_id in claim.contradicts:
            if other_id in by_id:
                key = tuple(sorted((claim.id, other_id)))
                if key not in seen:
                    seen.add(key)  # type: ignore[arg-type]
                    out.append((key[0], key[1], "explicit"))

    for i, a in enumerate(claims):
        for b in claims[i + 1:]:
            key = tuple(sorted((a.id, b.id)))
            if key in seen:
                continue
            shared = set(a.tags) & set(b.tags)
            opposed_on_option = bool(
                (set(a.supports_options) & set(b.opposes_options))
                or (set(a.opposes_options) & set(b.supports_options))
            )
            if shared and a.polarity != b.polarity and opposed_on_option:
                seen.add(key)  # type: ignore[arg-type]
                out.append((key[0], key[1], f"opposing polarity on {sorted(shared)[0]}"))
    return out


def partition(claims: tuple[Claim, ...]) -> dict[Grade, list[Claim]]:
    out: dict[Grade, list[Claim]] = {g: [] for g in Grade}
    for c in claims:
        out[c.grade].append(c)
    return out


def weight_share(claims: tuple[Claim, ...], grade: Grade, as_of: str | None,
                 tag_weights: dict[str, float]) -> float:
    """Share of total effective weight held by a given grade."""
    total = sum(effective_weight(c, as_of, tag_weights) for c in claims)
    if total <= 0:
        return 0.0
    part = sum(effective_weight(c, as_of, tag_weights) for c in claims if c.grade is grade)
    return part / total


def source_concentration(claims: tuple[Claim, ...], as_of: str | None,
                         tag_weights: dict[str, float]) -> tuple[str | None, float]:
    """Largest share of decisive weight attributable to a single source."""
    totals: dict[str, float] = {}
    grand = 0.0
    for c in claims:
        w = effective_weight(c, as_of, tag_weights)
        grand += w
        key = c.source or "<unsourced>"
        totals[key] = totals.get(key, 0.0) + w
    if grand <= 0 or not totals:
        return None, 0.0
    src, w = max(totals.items(), key=lambda kv: kv[1])
    return src, w / grand
