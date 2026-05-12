"""Module B: Experience Retriever — score and rank experiences against a JD."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from .jd_parser import JDAnalysis
from .run_manager import get_experiences_path


@dataclass(order=True)
class ScoredExperience:
    score: float = field(compare=True)
    experience: dict = field(compare=False)
    match_details: dict = field(default_factory=dict, compare=False)


def load_experiences(filepath: Optional[str] = None) -> list[dict]:
    """Load the experience database from a JSON file.

    Falls back to the project's default data/ directory.
    """
    path = filepath or str(get_experiences_path())
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def retrieve(
    jd: JDAnalysis,
    experiences: Optional[list[dict]] = None,
    target_role_filter: Optional[str] = None,
    min_score: float = 0.0,
) -> list[ScoredExperience]:
    """Retrieve experiences matching the given JD analysis.

    Parameters
    ----------
    jd : JDAnalysis
        Structured JD analysis.
    experiences : list[dict] | None
        Experience list; auto-loaded if None.
    target_role_filter : str | None
        Only keep experiences targeting this role.
    min_score : float
        Minimum score threshold [0-1].

    Returns
    -------
    list[ScoredExperience]
        Ranked results, highest score first.
    """
    if experiences is None:
        experiences = load_experiences()

    experiences = [e for e in experiences if not e.get("needs_verification", False)]

    if target_role_filter:
        experiences = [
            e
            for e in experiences
            if target_role_filter in e.get("target_roles", [])
            or "*" in e.get("target_roles", [])
        ]

    results: list[ScoredExperience] = []
    for exp in experiences:
        score, details = _score_experience(exp, jd)
        if score >= min_score:
            results.append(ScoredExperience(
                score=score,
                experience=exp,
                match_details=details,
            ))

    results.sort(reverse=True)
    return results


def _score_experience(exp: dict, jd: JDAnalysis) -> tuple[float, dict]:
    weights = jd.weights or {
        "tag_match": 0.30,
        "hard_requirement": 0.25,
        "industry_relevance": 0.20,
        "evidence_quality": 0.10,
        "recency": 0.15,
    }

    tag_score = _calc_tag_match(exp.get("tags", []), jd.keywords)
    hr_score = _calc_hard_requirement_match(exp, jd)
    industry_score = _calc_industry_relevance(exp, jd)
    evidence_score = _calc_evidence_quality(exp)
    recency_score = _calc_recency(exp)

    total = (
        weights.get("tag_match", 0.30) * tag_score
        + weights.get("hard_requirement", 0.25) * hr_score
        + weights.get("industry_relevance", 0.20) * industry_score
        + weights.get("evidence_quality", 0.10) * evidence_score
        + weights.get("recency", 0.15) * recency_score
    )

    details = {
        "tag_match": round(tag_score, 3),
        "hard_requirement": round(hr_score, 3),
        "industry_relevance": round(industry_score, 3),
        "evidence_quality": round(evidence_score, 3),
        "recency": round(recency_score, 3),
        "total": round(total, 3),
    }
    return total, details


def _calc_tag_match(exp_tags: list[str], jd_keywords: list[str]) -> float:
    if not jd_keywords or not exp_tags:
        return 0.0
    exp_lower = {t.lower().strip() for t in exp_tags}
    jd_lower = {k.lower().strip() for k in jd_keywords}
    intersection = exp_lower & jd_lower
    if not exp_lower:
        return 0.0
    return len(intersection) / len(exp_lower)


def _calc_hard_requirement_match(exp: dict, jd: JDAnalysis) -> float:
    if not jd.hard_requirements:
        return 1.0
    exp_text = json.dumps(exp, ensure_ascii=False).lower()
    matched = 0
    must_have_missed = False
    for hr in jd.hard_requirements:
        kw = hr.requirement.lower()
        if kw in exp_text:
            matched += 1
        elif hr.must_have:
            must_have_missed = True
    total = len(jd.hard_requirements)
    if total == 0:
        return 1.0
    if must_have_missed:
        return matched / total * 0.3
    return matched / total


def _calc_industry_relevance(exp: dict, jd: JDAnalysis) -> float:
    exp_text = json.dumps(exp, ensure_ascii=False).lower()
    score = 0.0
    if jd.keywords:
        matched = sum(1 for kw in jd.keywords if kw.lower() in exp_text)
        score = matched / len(jd.keywords)
    exp_roles = {r.lower() for r in exp.get("target_roles", [])}
    if "*" in exp_roles:
        score = max(score, 0.7)
    jd_title = jd.job_title.lower()
    for role in exp.get("target_roles", []):
        role_words = set(role.lower().replace(" ", ""))
        jd_words = set(jd_title.replace(" ", ""))
        if role_words & jd_words:
            score = max(score, 0.6)
    return min(score, 1.0)


def _calc_evidence_quality(exp: dict) -> float:
    level = exp.get("evidence_level", "")
    metrics = exp.get("metrics", [])
    has_verified_metrics = any(m.get("verified", False) for m in metrics)
    base = {"verified": 1.0, "plausible": 0.6, "anecdotal": 0.3}.get(level, 0.3)
    bonus = 0.15 if has_verified_metrics else 0.0
    return min(base + bonus, 1.0)


def _calc_recency(exp: dict) -> float:
    date_end = exp.get("date_end") or exp.get("date_start")
    if not date_end:
        return 0.5
    try:
        parts = str(date_end).split("-")
        if len(parts) != 2:
            return 0.5
        end = date(int(parts[0]), int(parts[1]), 1)
    except (ValueError, IndexError):
        return 0.5
    today = date.today()
    months_diff = (today.year - end.year) * 12 + (today.month - end.month)
    if months_diff <= 3:
        return 1.0
    elif months_diff <= 6:
        return 0.9
    elif months_diff <= 12:
        return 0.75
    elif months_diff <= 24:
        return 0.5
    else:
        return 0.3
