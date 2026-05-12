# Installation Guide

This guide is the source of truth for installing and validating the `resume-tailor` skill from scratch.

**v2.0:** This skill now uses a **4-skill architecture**. Install all 4 skills for full functionality.

Repository: `https://github.com/wangzichang224-design/resume-tailor-skill`

---

## Mode A: Claude Code (4-skill pipeline, recommended)

No Python needed. Claude does everything natively.

### Installation Steps

```bash
# 1. Create skill directories
mkdir -p ~/.claude/skills/resume-tailor \
         ~/.claude/skills/resume-jd-intake \
         ~/.claude/skills/resume-drafting \
         ~/.claude/skills/resume-review

# 2. Copy skill files (from repository root)
cp skills/resume-tailor/SKILL.md     ~/.claude/skills/resume-tailor/
cp skills/resume-jd-intake/SKILL.md  ~/.claude/skills/resume-jd-intake/
cp skills/resume-drafting/SKILL.md   ~/.claude/skills/resume-drafting/
cp skills/resume-review/SKILL.md     ~/.claude/skills/resume-review/

# 3. Copy templates and assets to resume-review (template resolution path)
cp -r assets ~/.claude/skills/resume-review/
cp -r templates ~/.claude/skills/resume-review/
```

### Set Up Experience Database

Create `data/my_experiences.local.json` in the project root. See `schemas/experience.schema.json` for the schema, or the README for an example.

### Set Up Template Path

The templates and CSS assets must be available at one of these locations:
1. `~/.claude/skills/resume-review/assets/resume-template/` — copied in step 3 above
2. `~/.claude/skills/resume-review/templates/` — copied in step 3 above

### PDF Export (Optional)

For automatic PDF generation:
```bash
pip install weasyprint
```
Without weasyprint, the skill saves an HTML file you can print to PDF in your browser.

### Verify Installation

Check that these files exist:
```bash
ls ~/.claude/skills/resume-tailor/SKILL.md
ls ~/.claude/skills/resume-jd-intake/SKILL.md
ls ~/.claude/skills/resume-drafting/SKILL.md
ls ~/.claude/skills/resume-review/SKILL.md
ls ~/.claude/skills/resume-review/assets/resume-template/style.css
ls ~/.claude/skills/resume-review/templates/zh/standard/style.css  # optional templates
```

---

## Mode B: Python Pipeline (for OpenClaw / 微信机器人 / shell-capable)

For platforms that can execute Python scripts. Uses the same 4-skill orchestration.

### Prerequisites

- Python >= 3.10
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/wangzichang224-design/resume-tailor-skill.git
cd resume-tailor-skill

# Install Python dependencies
pip install httpx weasyprint

# Install the 4 skill files into the skills directory
mkdir -p ~/.claude/skills/resume-tailor \
         ~/.claude/skills/resume-jd-intake \
         ~/.claude/skills/resume-drafting \
         ~/.claude/skills/resume-review

cp skills/resume-tailor/SKILL.md     ~/.claude/skills/resume-tailor/
cp skills/resume-jd-intake/SKILL.md  ~/.claude/skills/resume-jd-intake/
cp skills/resume-drafting/SKILL.md   ~/.claude/skills/resume-drafting/
cp skills/resume-review/SKILL.md     ~/.claude/skills/resume-review/

cp -r assets ~/.claude/skills/resume-review/
cp -r templates ~/.claude/skills/resume-review/
```

### Set Up Experience Database

```bash
mkdir -p data
# Place your experience data at data/my_experiences.local.json
```

**Format:** Array of experience objects per `schemas/experience.schema.json`

### Set Up .env for Screenshot Parsing (Optional)

Vision API is optional — you can paste JD text directly.

```
VISION_API_KEY=sk-your-qwen-api-key
VISION_API_PROVIDER=anthropic
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### Verify

```bash
python3 -c "from resume_tailor import run_pipeline; print('OK: package imported')"
```

---

## State Model

- `4-skill status`: `all-installed` | `partial` | `unavailable`
  - `all-installed`: all 4 SKILL.md files + `assets/resume-template/style.css` in place
- `python status`: `pip-installed` | `unavailable` (Mode B only)
- `pdf status`: `weasyprint-ready` | `html-only`
- `install result`: `strictly-validated` | `path-validated` | `incomplete`

### Validation Standard

`strictly-validated` requires ALL of:
- 4 SKILL.md files installed in correct paths
- `assets/resume-template/style.css` installed in resume-review skill directory
- Python package importable (Mode B only)
- Experience database exists at `data/my_experiences.local.json`

`incomplete` if:
- Any of the 4 SKILL.md files missing
- or assets or templates missing
