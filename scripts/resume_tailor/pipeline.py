"""Orchestration pipeline: JD parsing → retrieval → Markdown generation
→ LLM refinement → PDF export."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from .jd_parser import parse_jd, JDAnalysis
from .retriever import retrieve, load_experiences, ScoredExperience
from .md_generator import generate_markdown
from .run_manager import RunManager


def _load_deepseek_key() -> str | None:
    """Load DeepSeek API key from .env or environment."""
    candidates = [
        Path(__file__).resolve().parent.parent.parent / ".env",
        Path.home() / ".env",
    ]
    for env_path in candidates:
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("VISION_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("\"'")
    return None


def llm_refine_md(md_text: str, jd_text: str, api_key: str | None = None) -> str:
    """Use DeepSeek to polish resume bullet points for the target JD.

    Falls back to original text if API unavailable.
    """
    key = api_key or _load_deepseek_key()
    if not key:
        return md_text

    import httpx

    prompt = (
        "You are a professional resume writer. Polish the following resume "
        "to better match the job description. Follow these rules strictly:\n"
        "1. NEVER fabricate facts, numbers, company names, or skills.\n"
        "2. Make bullet points more concise and impactful.\n"
        "3. Prioritize experiences that match the JD keywords.\n"
        "4. Keep the overall Markdown structure intact (headers, sections).\n"
        "5. Output ONLY the polished Markdown, no commentary.\n\n"
        f"=== JOB DESCRIPTION ===\n{jd_text}\n\n"
        f"=== RESUME ===\n{md_text}"
    )

    try:
        response = httpx.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        text = ""
        for choice in data.get("choices", []):
            if choice.get("message"):
                text += choice["message"].get("content", "")
        return text.strip() or md_text
    except Exception as e:
        print(f"[resume-tailor] LLM refinement failed: {e}", file=sys.stderr)
        print("[resume-tailor] Using unrefined draft.", file=sys.stderr)
        return md_text


def run_pipeline(
    jd_text: str,
    job_title: Optional[str] = None,
    company: Optional[str] = None,
    target_role: Optional[str] = None,
    personal_info: Optional[dict] = None,
    min_score: float = 0.0,
    experiences: Optional[list[dict]] = None,
    run_manager: Optional[RunManager] = None,
    refine: bool = False,
    export_pdf: bool = False,
) -> str:
    """Full pipeline: JD text → (optionally refined) Markdown → (optionally) PDF.

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
    refine : bool
        Whether to apply LLM refinement.
    export_pdf : bool
        Whether to generate styled PDF after Markdown.

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

    # Step D: LLM Refinement (optional)
    if refine:
        print("[resume-tailor] Refining with LLM...")
        md = llm_refine_md(md, jd_text)
        md_path = manager.write("draft_resume.md", md)
        print(f"[resume-tailor] Refined resume → {md_path}")
    else:
        md_path = manager.write("draft_resume.md", md)
        print(f"[resume-tailor] Draft resume → {md_path}")

    print(f"[resume-tailor] JD analysis → {manager.dir / 'jd_analysis.json'}")
    print(f"[resume-tailor] Selected experiences → {manager.dir / 'selected_experiences.json'}")

    # Step E: PDF Export (optional)
    if export_pdf:
        try:
            from .export_pdf import export_pdf as _export_pdf
            pdf_path = _export_pdf(md_path)
            print(f"[resume-tailor] PDF generated → {pdf_path}")
        except Exception as e:
            print(f"[resume-tailor] PDF export failed: {e}", file=sys.stderr)
            print("[resume-tailor] Install weasyprint: pip install weasyprint", file=sys.stderr)

    print(f"[resume-tailor] ── Edit {md_path.name}, then run build_pdf to re-export PDF ──")

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
    parser.add_argument("--refine", action="store_true", help="Apply LLM refinement to bullet points")
    parser.add_argument("--pdf", action="store_true", help="Export styled PDF after generation")

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
        refine=args.refine,
        export_pdf=args.pdf,
    )

    print(md)


if __name__ == "__main__":
    main()
