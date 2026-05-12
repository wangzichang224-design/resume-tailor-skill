"""Module C: Markdown Generator — render scored experiences into resume Markdown."""

from __future__ import annotations

from typing import Optional

from .retriever import ScoredExperience, JDAnalysis


def _fmt_date(date_str: Optional[str]) -> str:
    if not date_str:
        return "至今"
    try:
        parts = date_str.split("-")
        return f"{parts[0]}.{parts[1]}"
    except (IndexError, ValueError):
        return date_str


def _fmt_date_range(start: Optional[str], end: Optional[str]) -> str:
    s = _fmt_date(start)
    e = _fmt_date(end) if end else "至今"
    return f"{s} - {e}"


def _render_star_bullets(exp: dict) -> list[str]:
    star = exp.get("star_details", {})
    bullets: list[str] = []
    for key in ("situation", "task", "action", "result"):
        text = (star.get(key) or "").strip()
        if text:
            bullets.append(text)
    if not bullets:
        bullets = exp.get("highlights", [])[:3]
    metrics = exp.get("metrics", [])
    for m in metrics:
        metric_name = m.get("metric", "")
        metric_val = m.get("value", "")
        if metric_name and metric_val:
            bullets.append(f"● {metric_name}：{metric_val}")
    return bullets


def generate_markdown(
    jd: JDAnalysis,
    results: list[ScoredExperience],
    personal_info: Optional[dict] = None,
) -> str:
    """Generate a complete Markdown resume from JD analysis and scored experiences.

    Parameters
    ----------
    jd : JDAnalysis
        Structured JD analysis.
    results : list[ScoredExperience]
        Ranked experience list.
    personal_info : dict | None
        Optional personal info: name, phone, email, location, title.

    Returns
    -------
    str
        Markdown resume text.
    """
    lines: list[str] = []

    # Header
    info = personal_info or {}
    name = info.get("name", "姓名")
    title_line = info.get("title", jd.job_title)
    lines.append(f"# {name}")
    lines.append(f"**{title_line}**")
    lines.append("")

    contact_parts = []
    for field in ["phone", "email", "location"]:
        if info.get(field):
            contact_parts.append(info[field])
    if contact_parts:
        lines.append(" | ".join(contact_parts))
        lines.append("")

    lines.append("---")
    lines.append("")

    # Group by category
    category_order = ["education", "project", "internship", "work", "certification", "skill"]
    category_label = {
        "education": "教育经历",
        "project": "项目经历",
        "internship": "实习经历",
        "work": "工作经历",
        "certification": "证书",
        "skill": "专业技能",
    }

    grouped: dict[str, list[ScoredExperience]] = {c: [] for c in category_order}
    for r in results:
        cat = r.experience.get("category", "")
        if cat in grouped:
            grouped[cat].append(r)

    # Render each category
    for cat in category_order:
        items = grouped[cat]
        if not items:
            continue

        section_lines: list[str] = []
        section_lines.append(f"## {category_label.get(cat, cat)}")
        section_lines.append("")

        for idx, scored in enumerate(items):
            exp = scored.experience
            title = exp.get("title", "")
            subtitle = exp.get("subtitle", "")
            date_range = _fmt_date_range(exp.get("date_start"), exp.get("date_end"))

            if subtitle:
                section_lines.append(f"### {title}")
                section_lines.append(f"**{subtitle}** · {date_range}")
            else:
                section_lines.append(f"### {title} · {date_range}")
            section_lines.append("")

            bullets = _render_star_bullets(exp)
            for b in bullets:
                section_lines.append(f"- {b}")

            if idx < len(items) - 1:
                section_lines.append("")

        section_lines.append("")
        lines.extend(section_lines)

    # Keyword cloud
    if jd.keywords:
        lines.append("---")
        lines.append("")
        lines.append(f"**关键词匹配**：{'、'.join(jd.keywords[:10])}")
        lines.append("")

    return "\n".join(lines)
