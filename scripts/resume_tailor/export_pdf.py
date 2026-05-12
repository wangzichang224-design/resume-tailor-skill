"""PDF Export — convert refined Markdown to styled PDF.

Uses weasyprint (HTML → PDF) with an optional Pandoc step for Markdown → HTML.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def _get_template_dir() -> Path:
    """Return the assets/resume-template directory."""
    return Path(__file__).resolve().parent.parent.parent / "assets" / "resume-template"


def _md_to_html_via_pandoc(md_path: Path, css_path: Path | None = None) -> str:
    """Convert Markdown to HTML using Pandoc."""
    cmd = ["pandoc", str(md_path), "-f", "markdown", "-t", "html", "--self-contained"]
    if css_path:
        cmd += ["--css", str(css_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"Pandoc HTML conversion failed: {result.stderr}")
    return result.stdout.strip()


def _md_to_html_simple(md_path: Path, css_path: Path | None = None) -> str:
    """Simple Markdown to HTML conversion (no Pandoc dependency)."""
    md = md_path.read_text(encoding="utf-8")
    lines = md.splitlines()
    html_parts: list[str] = []

    css = ""
    if css_path and css_path.exists():
        css = css_path.read_text(encoding="utf-8")

    in_ul = False
    for line in lines:
        stripped = line.strip()

        # Header
        if stripped.startswith("# ") and not stripped.startswith("## "):
            html_parts.append(f"<h1>{stripped[2:]}</h1>")
        elif stripped.startswith("## "):
            if in_ul:
                html_parts.append("</ul>")
                in_ul = False
            html_parts.append(f"<h2>{stripped[3:]}</h2>")

        # Separator
        elif stripped == "---":
            if in_ul:
                html_parts.append("</ul>")
                in_ul = False
            html_parts.append("<hr>")

        # Bullet
        elif stripped.startswith("- "):
            if not in_ul:
                html_parts.append("<ul>")
                in_ul = True
            html_parts.append(f"<li>{stripped[2:]}</li>")

        # Bold entry header
        elif stripped.startswith("**") and stripped.endswith("**"):
            if in_ul:
                html_parts.append("</ul>")
                in_ul = False
            html_parts.append(f"<p>{stripped}</p>")

        # Plain text
        elif stripped:
            if in_ul:
                html_parts.append("</ul>")
                in_ul = False
            html_parts.append(f"<p>{stripped}</p>")

        # Empty line
        else:
            if in_ul:
                html_parts.append("</ul>")
                in_ul = False

    if in_ul:
        html_parts.append("</ul>")

    body = "\n".join(html_parts)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
{css}
</style>
</head>
<body>
{body}
</body>
</html>"""


def export_pdf(md_path: Path, output_path: Path | None = None) -> Path:
    """Convert a Markdown resume file to a styled PDF.

    Parameters
    ----------
    md_path : Path
        Path to the Markdown file.
    output_path : Path | None
        Output PDF path (defaults to md_path with .pdf extension).

    Returns
    -------
    Path
        Path to the generated PDF.
    """
    if output_path is None:
        output_path = md_path.with_suffix(".pdf")

    template_dir = _get_template_dir()
    css_path = template_dir / "style.css"

    # Convert Markdown to HTML
    try:
        html_content = _md_to_html_via_pandoc(md_path, css_path)
        # Wrap in template if available
        tmpl_path = template_dir / "template.html"
        if tmpl_path.exists():
            css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
            tmpl = tmpl_path.read_text(encoding="utf-8")
            html_content = tmpl.replace("{{CSS}}", css).replace("{{CONTENT}}", html_content)
    except (FileNotFoundError, OSError):
        # Pandoc not available — use built-in converter
        html_content = _md_to_html_simple(md_path, css_path)

    # Write HTML and convert to PDF via weasyprint
    import weasyprint
    weasyprint.HTML(string=html_content).write_pdf(str(output_path))

    return output_path
