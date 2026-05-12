---
name: resume-jd-intake
description: >
  Intake a job description (screenshot or pasted text), load the local experience
  database, confirm uncertain information with the user, and prepare structured
  data for the drafting phase.
---

# Resume JD Intake

Read the JD and experience database, clarify unknowns, and write structured intake artifacts into the workspace.

## Skill Boundary

- **Allowed:** `resume-jd-intake` only.
- **Forbidden:** all other skills.

## Workspace Contract

Receive a workspace path from the orchestrator. Write output into `<workspace>/work/`.

## Step 1. Read the JD

- If the user provides a **screenshot file path**, use the Read tool to extract all text from the image.
- If the user **pastes JD text**, use it directly.
- Save the raw JD text as `work/jd_text.md`.

## Step 2. Load the Experience Database

Read the JSON file from one of these locations (try in order):
1. `data/my_experiences.local.json` (project root relative to skills directory)
2. Ask the user for the path explicitly

The JSON should be an array of experience objects following the schema in `schemas/experience.schema.json`.

**Key fields per experience:**
| Field | Description | Required |
|-------|-------------|----------|
| `id` | Unique identifier | Yes |
| `category` | `education` / `project` / `internship` / `work` / `skill` | Yes |
| `title` | Company, project, or school name | Yes |
| `subtitle` | Role, degree, or subtitle | No |
| `date_start` / `date_end` | `YYYY-MM` format | Recommended |
| `tags` | Keywords for JD matching | Recommended |
| `star_details` | `situation` / `task` / `action` / `result` | Yes |
| `evidence_level` | `verified` / `plausible` / `anecdotal` | Recommended |
| `needs_verification` | If true, **excluded** from output | No |
| `target_roles` | Applicable target roles | Yes |
| `metrics` | Quantitative metrics (`verified` boolean for bonus) | No |
| `highlights` | Suggested bullet phrasings | No |

## Step 3. Confirm Information (Only When Necessary)

**Rule: If the information is already in the experience database, use it directly — do NOT ask.**

This includes:
- Phone number (if present in any experience entry's fields)
- Email address (if present)
- Location
- Dates, titles, subtitles
- Metrics, numbers, evidence

**Only ask when information is genuinely missing or ambiguous:**
- "你的简历库里没有手机号，方便提供吗？"
- "这个项目只写了开始时间，结束时间是什么时候？"

**Do not fabricate.** If info is missing, ask. If the user says "just use what's there", proceed.

## Step 4. Write Intake Artifacts

### `work/jd_analysis.json`

Analyze the JD text and produce this structure:

```json
{
  "job_title": "岗位名称",
  "company": "公司名（可选）",
  "hard_requirements": [
    {"requirement": "具体硬性要求", "must_have": true}
  ],
  "soft_skills": ["协作", "沟通"],
  "keywords": ["AI", "大模型", "产品经理"],
  "pain_points": ["关键痛点"],
  "weights": {
    "tag_match": 0.30,
    "hard_requirement": 0.25,
    "industry_relevance": 0.20,
    "evidence_quality": 0.10,
    "recency": 0.15
  }
}
```

**Weight inference rules:**
- Default weights as above.
- **Tech-focused JD** (LLM, NLP, Python, 开发): `tag_match→0.35`, `hard_requirement→0.30`, `industry_relevance→0.15`, `recency→0.10`
- **Audit/Finance-focused JD** (审计, 财务, 会计): `industry_relevance→0.30`, `tag_match→0.25`, `evidence_quality→0.15`
- **Data-focused JD** (数据分析, 数据驱动): `hard_requirement→0.30`, `tag_match→0.30`

### `work/experiences.json`

Write the full experience database as a JSON array. Filter out entries with `needs_verification: true`.

### `work/intake-summary.md`

Write a Markdown summary of what was ingested:
- JD source (screenshot / text)
- Job title
- Number of experiences loaded (by category)
- Any confirmations the user provided
- Any flags/notes for the drafting phase
