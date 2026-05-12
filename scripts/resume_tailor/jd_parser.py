"""Module A: JD Parser — parse raw JD text into structured JDAnalysis.

Pure-text, rule-based. No images or PDFs.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class HardRequirement:
    requirement: str
    must_have: bool = True


@dataclass
class JDAnalysis:
    """Structured JD analysis, conforming to jd_analysis.schema.json."""

    job_title: str = ""
    company: str = ""
    hard_requirements: list[HardRequirement] = field(default_factory=list)
    soft_skills: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    pain_points: list[str] = field(default_factory=list)
    weights: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "job_title": self.job_title,
            "company": self.company,
            "hard_requirements": [
                {"requirement": r.requirement, "must_have": r.must_have}
                for r in self.hard_requirements
            ],
            "soft_skills": self.soft_skills,
            "keywords": self.keywords,
            "pain_points": self.pain_points,
            "weights": self.weights,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


# ── Keyword & industry lexicon ──────────────────────────────────────

_HARD_REQUIREMENT_PATTERNS: list[tuple[str, bool]] = [
    (r"(硕士|研究生|博士|本科)", True),
    (r"(英语.*[读写听说流利熟练]|英文.*[读写听说流利熟练]|CET[46]|雅思|托福)", True),
    (r"(Python|SQL|Excel|Tableau|Power BI|Axure|Figma|Sketch|Java|C\+\+|Go)", True),
    (r"(LLM|AI|NLP|机器学习|深度学习|数据分析|数据挖掘)", False),
    (r"(审计|企业会计准则|财务分析|跨境电商|商业分析)", False),
    (r"(\d+\+?\s*年.*经验|实习.*经验|产品.*经验)", True),
]

_SOFT_SKILL_PATTERNS: list[str] = [
    r"(沟通|协作|团队|合作|逻辑|分析|学习|自驱|owner|ownership)",
    r"(抗压|执行力|推动|落地|细节|责任心|创新|积极主动)",
]

_SECTION_KEYWORDS: dict[str, list[str]] = {
    "技术": ["Python", "SQL", "LLM", "NLP", "API", "算法", "架构", "后端", "前端", "开发"],
    "产品": ["产品", "需求", "PRD", "原型", "Axure", "用户", "增长", "迭代", "roadmap"],
    "数据": ["数据分析", "数据驱动", "指标", "A/B测试", "报表", "挖掘"],
    "运营": ["运营", "活动", "内容", "用户增长", "裂变", "私域"],
    "审计": ["审计", "底稿", "会计", "财报", "上市公司", "年审"],
}


# ── Core functions ──────────────────────────────────────────────────


def parse_jd(
    jd_text: str,
    job_title: Optional[str] = None,
    company: Optional[str] = None,
) -> JDAnalysis:
    """Parse raw JD text into a structured JDAnalysis."""
    analysis = JDAnalysis()

    analysis.job_title = job_title or _extract_job_title(jd_text)
    analysis.company = company or ""

    # Hard requirements
    seen_reqs: set[str] = set()
    for pattern, must_have in _HARD_REQUIREMENT_PATTERNS:
        for match in re.finditer(pattern, jd_text, re.IGNORECASE):
            text = match.group(0).strip()
            if text and text not in seen_reqs:
                seen_reqs.add(text)
                analysis.hard_requirements.append(
                    HardRequirement(requirement=text, must_have=must_have)
                )

    # Soft skills
    seen_soft: set[str] = set()
    for pattern in _SOFT_SKILL_PATTERNS:
        for match in re.finditer(pattern, jd_text, re.IGNORECASE):
            text = match.group(0).strip().lower()
            if text and text not in seen_soft:
                seen_soft.add(text)
                analysis.soft_skills.append(match.group(0).strip())

    # Keywords
    seen_kw: set[str] = set()
    for cat, words in _SECTION_KEYWORDS.items():
        for word in words:
            if word.lower() in jd_text.lower() and word not in seen_kw:
                seen_kw.add(word)
                analysis.keywords.append(word)

    analysis.pain_points = _extract_pain_points(jd_text)
    analysis.weights = _infer_weights(analysis)

    return analysis


def _extract_job_title(text: str) -> str:
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    for line in lines[:5]:
        m = re.search(r"(招聘|职位|岗位)[：:]\s*(.+)", line)
        if m:
            return m.group(2).strip()
        if 2 < len(line) < 30 and not re.search(r"[，。；：、]", line):
            return line
    return ""


def _extract_pain_points(text: str) -> list[str]:
    points: list[str] = []
    _PAIN_KEYWORDS = ["痛点", "挑战", "问题", "难点", "不足", "现状"]
    for keyword in _PAIN_KEYWORDS:
        pattern = rf"{keyword}[：:]\s*([^。\n]+)"
        for match in re.finditer(pattern, text):
            points.append(match.group(1).strip())
    if not points:
        for match in re.finditer(r"(解决|优化|提升|改善|处理|应对)\s*([^，。\n]{4,30})", text):
            points.append(match.group(0).strip())
            if len(points) >= 3:
                break
    return points[:5]


def _infer_weights(analysis: JDAnalysis) -> dict[str, float]:
    weights = {
        "tag_match": 0.30,
        "hard_requirement": 0.25,
        "industry_relevance": 0.20,
        "evidence_quality": 0.10,
        "recency": 0.15,
    }
    kw_lower = [k.lower() for k in analysis.keywords]

    if any(w in kw_lower for w in ["llm", "nlp", "python", "算法", "架构", "开发"]):
        weights["tag_match"] = 0.35
        weights["hard_requirement"] = 0.30
        weights["industry_relevance"] = 0.15
        weights["evidence_quality"] = 0.10
        weights["recency"] = 0.10

    if any(w in kw_lower for w in ["审计", "底稿", "会计", "财务"]):
        weights["industry_relevance"] = 0.30
        weights["tag_match"] = 0.25
        weights["evidence_quality"] = 0.15

    if any(w in kw_lower for w in ["数据分析", "数据驱动", "挖掘"]):
        weights["hard_requirement"] = 0.30
        weights["tag_match"] = 0.30

    return weights


def parse_jd_from_file(filepath: str) -> JDAnalysis:
    """Read and parse a .txt JD file."""
    if not filepath.endswith(".txt"):
        raise ValueError(f"JD parser only accepts .txt files, got: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return parse_jd(f.read())
