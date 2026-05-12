"""Orchestration pipeline: JD parsing → retrieval → Markdown generation → PDF build."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from .jd_parser import parse_jd, JDAnalysis
from .retriever import retrieve, load_experiences, ScoredExperience
from .md_generator import generate_markdown
from .run_manager import RunManager


def run_pipeline(
    jd_text: str,
    job_title: Optional[str] = None,
    company: Optional[str] = None,
    target_role: Optional[str] = None,
    personal_info: Optional[dict] = None,
    min_score: float = 0.0,
    experiences: Optional[list[dict]] = None,
    run_manager: Optional[RunManager] = None,
) -> str:
    """Full pipeline: JD text → Markdown resume.

    Parameters
    ----------
    jd_text : str
        Raw JD text.
    job_title : str | None
        Job title (auto-extracted if None).
    company : str | None
        Company name.
    target_role : str | None
        Filter experiences by target role (e.g. "AI产品经理").
    personal_info : dict | None
        Optional fields: name, phone, email, location, title.
    min_score : float
        Minimum retrieval score threshold.
    experiences : list[dict] | None
        Experience database (auto-loaded if None).
    run_manager : RunManager | None
        Run output directory manager.

    Returns
    -------
    str
        Generated Markdown resume.
    """
    manager = run_manager or RunManager()

    # Step A: Parse JD
    jd = parse_jd(jd_text, job_title=job_title, company=company)
    manager.write_json("jd_analysis.json", jd.to_dict())
    manager.write("jd_text.md", jd_text)

    # Step B: Retrieve experiences
    results = retrieve(
        jd,
        experiences=experiences,
        target_role_filter=target_role,
        min_score=min_score,
    )
    selected = [
        {
            "id": r.experience.get("id"),
            "score": r.score,
            "match_details": r.match_details,
            "experience": r.experience,
        }
        for r in results
    ]
    manager.write_json("selected_experiences.json", selected)

    # Step C: Generate Markdown
    md = generate_markdown(jd, results, personal_info=personal_info)
    md_path = manager.write("draft_resume.md", md)

    print(f"[resume-tailor] JD analysis → {manager.dir / 'jd_analysis.json'}")
    print(f"[resume-tailor] Selected experiences → {manager.dir / 'selected_experiences.json'}")
    print(f"[resume-tailor] Draft resume → {md_path}")
    print(f"[resume-tailor] ── Manual edit {md_path.name}, then run build_pdf to export PDF ──")

    return md


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="resume-tailor: tailor your resume for a JD")
    parser.add_argument("jd_file", nargs="?", type=str, help="Path to JD .txt file")
    parser.add_argument("--image", type=str, help="Path to JD screenshot (requires vision API)")
    parser.add_argument("--title", type=str, help="Job title (auto-extracted if omitted)")
    parser.add_argument("--company", type=str, help="Company name")
    parser.add_argument("--role", type=str, help="Target role filter")
    parser.add_argument("--name", type=str, default="姓名", help="Your name")
    parser.add_argument("--phone", type=str, help="Phone number")
    parser.add_argument("--email", type=str, help="Email address")
    parser.add_argument("--location", type=str, help="Location")
    parser.add_argument("--min-score", type=float, default=0.0, help="Minimum score threshold")
    parser.add_argument("--output-dir", type=str, help="Output directory (auto-created if omitted)")

    args = parser.parse_args()

    # Read JD text
    if args.image:
        try:
            from .jd_image import parse_jd_image
            jd_text = parse_jd_image(args.image)
        except Exception as e:
            print(f"[resume-tailor] Vision API failed: {e}", file=sys.stderr)
            print("[resume-tailor] Falling back: please paste the JD text manually.", file=sys.stderr)
            sys.exit(1)
    elif args.jd_file:
        path = Path(args.jd_file)
        if not path.exists():
            print(f"File not found: {path}", file=sys.stderr)
            sys.exit(1)
        if path.suffix not in (".txt", ".md"):
            print(f"Only .txt/.md files supported, got: {path.suffix}", file=sys.stderr)
            sys.exit(1)
        jd_text = path.read_text(encoding="utf-8")
    else:
        jd_text = sys.stdin.read()

    if not jd_text.strip():
        print("Error: empty JD text", file=sys.stderr)
        sys.exit(1)

    personal_info = {}
    if args.name:
        personal_info["name"] = args.name
    if args.phone:
        personal_info["phone"] = args.phone
    if args.email:
        personal_info["email"] = args.email
    if args.location:
        personal_info["location"] = args.location

    manager = RunManager(output_dir=args.output_dir)
    md = run_pipeline(
        jd_text=jd_text,
        job_title=args.title,
        company=args.company,
        target_role=args.role,
        personal_info=personal_info or None,
        min_score=args.min_score,
        run_manager=manager,
    )

    print(md)


if __name__ == "__main__":
    main()
