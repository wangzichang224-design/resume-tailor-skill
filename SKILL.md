---
name: resume-tailor
description: >
  Use when the user wants to tailor their resume for a specific job description (JD).
  Accepts JD as text or screenshot. Outputs a customized Markdown resume and optionally a PDF.
  Chinese-first, bilingual triggers.
---

# Resume Tailor

> **v2.0** — This skill has been restructured into a 4-skill pipeline.
> See `skills/` for the individual skill definitions, or `README.md` for the full guide.

## Quick Install

For **Claude Code**, install the 4 skills:

```bash
mkdir -p ~/.claude/skills/resume-tailor \
         ~/.claude/skills/resume-jd-intake \
         ~/.claude/skills/resume-drafting \
         ~/.claude/skills/resume-review

cp skills/resume-tailor/SKILL.md     ~/.claude/skills/resume-tailor/
cp skills/resume-jd-intake/SKILL.md  ~/.claude/skills/resume-jd-intake/
cp skills/resume-drafting/SKILL.md   ~/.claude/skills/resume-drafting/
cp skills/resume-review/SKILL.md     ~/.claude/skills/resume-review/

# Copy templates
cp -r assets ~/.claude/skills/resume-review/
cp -r templates ~/.claude/skills/resume-review/
```

For **OpenClaw / 微信机器人** — see `INSTALL.md` for the Python pipeline setup.

## What's New in v2.0

- **4-skill pipeline**: `resume-tailor` (orchestrator) → `resume-jd-intake` (JD + experience loading) → `resume-drafting` (scoring + writing) → `resume-review` (audit + PDF)
- **Claim-Source-Map**: every bullet in the resume is traced back to its source
- **Information confirmation**: the skill asks about unclear data before writing
- **Multi-template**: Chinese standard, English ATS, Academic research templates
- **Polished CSS**: professional single-column layout, A4-optimized
- **Still privacy-first**: experience database stays local

## Quick Start

1. Make sure your experience database is ready at `data/my_experiences.local.json`
2. Ask Claude Code:

```
帮我根据这个 JD 截图定制简历
```

Or:

```
tailor my resume for this job description
```
