---
name: resume-tailor
description: >
  Orchestrate a multi-skill resume workflow: intake a job description, load your
  experience database, score and match experiences, draft a tailored resume in
  Markdown, review claims for factual safety, and export a polished PDF.
  Chinese-first, bilingual triggers.
---

# Resume Tailor

Coordinate a **four-skill pipeline** that turns a job description (screenshot or text) into a **fact-backed, JD-tailored PDF resume**.

**Core principle:** privacy-first, no fabrication, every claim traceable to source material.

---

## Skill Boundary

- **Allowed:** `resume-tailor` (orchestrator), `resume-jd-intake`, `resume-drafting`, `resume-review`
- **Forbidden:** all other skills

---

## Workflow

```
User presents JD (screenshot or text)
  │
  ├─ [resume-jd-intake]  Read JD, load experience DB, confirm unknowns
  │
  ├─ [resume-drafting]   Analyze JD, score experiences, write draft
  │
  └─ [resume-review]     Review claims, generate HTML, export PDF
```

### Step 1. Create Workspace

Create `resume-workspace-YYYYMMDD-HHMMSS/` in the current directory.
Inside it, create `work/` and `output/` subdirectories.

### Step 2. Invoke resume-jd-intake

Tell the user the intake phase is starting. Then invoke `resume-jd-intake`.

### Step 3. Invoke resume-drafting

After intake completes, invoke `resume-drafting` and pass the workspace path.

### Step 4. Invoke resume-review

After drafting completes, invoke `resume-review` and pass the workspace path.

### Step 5. Report

Report the final output paths:
```
output/resume.pdf
output/resume.html
work/claim-source-map.md
```

## When to Use

Use this skill when the user wants any of the following:

- "根据这个 JD 截图定制简历"
- "tailor my resume for this job"
- "把这个 JD 转成匹配的简历"
- "帮我根据这个岗位定制简历"
- "帮我做一份匹配这个 JD 的简历"

Do **not** use this skill for:
- general resume writing advice without a specific JD
- writing cover letters
- job search queries without tailoring an existing experience database

## Non-Negotiables

- **NO FABRICATION.** Never invent experience, metrics, company names, or personal info.
- **`needs_verification: true` entries are FORBIDDEN** in the output.
- **Never auto-submit** to any job portal.
- **All claims must be traceable** to the experience database or user confirmation.
- **Privacy boundary:** all artifacts go inside the workspace. Never scatter files.
