# Installation Guide

This guide is the source of truth for installing and validating the `resume-tailor` skill from scratch.

Repository: `https://github.com/wangzichang224-design/resume-tailor-skill`

Raw files:
- `https://raw.githubusercontent.com/wangzichang224-design/resume-tailor-skill/main/SKILL.md`
- `https://raw.githubusercontent.com/wangzichang224-design/resume-tailor-skill/main/INSTALL.md`
- `https://raw.githubusercontent.com/wangzichang224-design/resume-tailor-skill/main/README.md`
- `https://raw.githubusercontent.com/wangzichang224-design/resume-tailor-skill/main/LICENSE`

State model:
- `python status`: `pip-installed` | `unavailable`
- `pdf status`: `chrome-ready` | `pandoc-only` | `unavailable`
- `vision key`: `configured` | `missing` (non-blocking; falls back to manual paste)
- `install result`: `strictly validated` | `path-validated` | `incomplete`

Important naming rule:
- the repository name is `resume-tailor-skill`
- the installed local skill folder must be `resume-tailor`
- do not install into a folder named `resume-tailor-skill`

## For Humans

Copy and paste this prompt to your LLM agent:

```text
Install and validate the `resume-tailor` skill by following this guide exactly:
https://raw.githubusercontent.com/wangzichang224-design/resume-tailor-skill/main/INSTALL.md
```

## For LLM Agents

Follow this order exactly.

### 1. Detect the host agent family

Use one of:
- `Claude Code` if the environment refers to `~/.claude/skills/`
- `OpenCode` if the environment refers to `~/.config/opencode/skills/`
- `.agents/skills style setup` if the environment uses `.agents/skills/`

### 2. Resolve the skills directory

- `Claude Code` → `~/.claude/skills/`
- `OpenCode` → `~/.config/opencode/skills/`
- `.agents/skills` → `~/.agents/skills/`

### 3. Create `<skills-dir>/resume-tailor/`

### 4. Install skill files from raw URLs

Download these files into `<skills-dir>/resume-tailor/`:
- `SKILL.md`
- `README.md`
- `LICENSE`

### 5. Verify SKILL.md exists

Confirm `<skills-dir>/resume-tailor/SKILL.md` exists.

If the host caches skills per session, restart/reload now.

### 6. Install the Python package

```bash
# Clone or copy the repository
git clone https://github.com/wangzichang224-design/resume-tailor-skill.git
cd resume-tailor-skill

# Install the Python package
pip install -e .

# Or for development: pip install -e ".[dev]"
```

### 7. Set up the private experience database

```bash
# Create the data directory
mkdir -p data

# Copy your existing experience database
# (expected format: array of experience objects per schemas/experience.schema.json)
# Save as data/my_experiences.local.json (auto-detected, gitignored)
```

### 8. Configure vision API (optional)

Create or edit `.env` in the project root:

```
VISION_API_KEY=sk-your-api-key
VISION_API_PROVIDER=anthropic
```

Supported providers: `anthropic` (Claude), `openai` (GPT-4o)

If not configured, the skill will gracefully fall back to:
- saving the screenshot to the run directory
- asking the user to paste the JD text manually

### 9. Check PDF build environment

Test in this order:
- `google-chrome --version` or `chromium --version` or `msedge --version`
- `pandoc --version`

Classify as:
- `chrome-ready`: Chrome/Chromium/Edge + Pandoc both available
- `pandoc-only`: Pandoc available, no browser
- `unavailable`: neither available

Missing Chrome/Pandoc means PDF export is blocked, but **Markdown output still works**. The minimum viable deliverable is the Markdown draft.

### 10. Verify installation

Run the smoke test:

```bash
python -c "from resume_tailor import run_pipeline; print('OK: package imported')"

python -m pytest tests/ -v  # if tests/ exists
```

### 11. Report the final result

Report:
- detected agent family
- resolved skills directory
- installed skill path
- whether the Python package is `pip-installed` or `unavailable`
- whether PDF build is `chrome-ready`, `pandoc-only`, or `unavailable`
- whether vision API key is `configured` or `missing`
- whether the `install result` is `strictly validated`, `path-validated`, or `incomplete`

## Validation Standard

`strictly validated` requires ALL of:
- `<skills-dir>/resume-tailor/SKILL.md` exists
- Python package imports successfully
- `data/my_experiences.local.json` exists (or `.json`)

`path-validated` requires:
- skill files placed and import works

`incomplete` if:
- Python import fails
- skill files not properly placed

Missing Chrome/Pandoc or missing vision API key do NOT reduce the validation tier — these are runtime capabilities, not installation criteria.
