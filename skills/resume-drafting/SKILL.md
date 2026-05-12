---
name: resume-drafting
description: >
  Analyze a structured JD, score experiences against it, rank them, and write a
  tailored Markdown resume draft.
---

# Resume Drafting

Score and rank experiences from the intake phase, then render a JD-tailored Markdown resume.

## Skill Boundary

- **Allowed:** `resume-drafting` only.
- **Forbidden:** all other skills.

## Workspace Contract

Read from `<workspace>/work/`: `jd_analysis.json`, `experiences.json`, `intake-summary.md`
Write into `<workspace>/work/`: `scored-experiences.json`, `draft-resume.md`

## Step 1. Score Experiences

Score each experience against the JD using **5 dimensions**. Compute a weighted total for each.

### Dimension 1: Tag Match (weight: 0.30)

Compare experience tags against JD keywords.
- `score = matching_tags / total_exp_tags` (case-insensitive)
- If either list is empty: `score = 0.0`

### Dimension 2: Hard Requirement Match (weight: 0.25)

Check if experience text (title, subtitle, star_details, tags, highlights) contains each hard requirement keyword.
- `score = matched_reqs / total_reqs`
- If a `must_have` requirement is missed: `score = score * 0.3` (70% penalty)
- If no hard requirements exist: `score = 1.0`

### Dimension 3: Industry Relevance (weight: 0.20)

Check JD keywords against the full experience text.
- `score = matched_keywords / total_keywords`
- If `target_roles` contains `"*"`: floor at 0.7
- If any target_role word-characters overlap with job_title word-characters: floor at 0.6
- Cap at 1.0

### Dimension 4: Evidence Quality (weight: 0.10)

Based on `evidence_level`:
- `verified` = 1.0
- `plausible` = 0.6
- `anecdotal` = 0.3 (default)
- +0.15 bonus if any metric has `verified: true`
- Cap at 1.0

### Dimension 5: Recency (weight: 0.15)

Calculate months from `date_end` (or `date_start` if end missing) to today:
- ≤ 3 months → 1.0
- ≤ 6 months → 0.9
- ≤ 12 months → 0.75
- ≤ 24 months → 0.50
- > 24 months → 0.30
- Missing date → 0.50

### Total Score

```
total = (tag_match * 0.30) + (hard_requirement * 0.25) + (industry_relevance * 0.20) + (evidence_quality * 0.10) + (recency * 0.15)
```

### Filtering Rules
- Entries with `needs_verification: true` are already filtered out by intake — do not reintroduce them.
- Apply `min_score` threshold (default 0.0).
- Sort by total score descending.

## Step 2. Write Scored Experiences

Save `work/scored-experiences.json`:
```json
[
  {
    "id": "exp_id",
    "score": 0.85,
    "match_details": {
      "tag_match": 0.5,
      "hard_requirement": 1.0,
      "industry_relevance": 0.8,
      "evidence_quality": 1.0,
      "recency": 1.0,
      "total": 0.85
    },
    "experience": { ... }
  }
]
```

## Step 3. Write Draft Resume

Write `work/draft-resume.md` following this exact format:

```markdown
# Name
**Title**
contact info

---

## 教育

**School | Degree** · 2025.09 – 2027.06
- Bullet 1
- Bullet 2

## 项目经历

**Project Name | Role** · 2025.12 – 2026.02
- Context (situation + task combined)
- Action taken
- Result achieved（Metric: value）

## 实习经历

**Company | Role** · 2025.10 – 2026.01
- Bullet points (max 4)
```

### Format Rules

**Category order:** `education → project → internship → work → skill`

**Category labels:**
| Key | Label |
|-----|-------|
| education | 教育 |
| project | 项目经历 |
| internship | 实习经历 |
| work | 工作经历 |
| skill | 专业技能 |

**Entry header format:**
- `**Title | Subtitle** · Date` if subtitle exists
- `**Title** · Date` if no subtitle

**Date format:** `YYYY.MM – YYYY.MM` (e.g., "2025.09 – 2026.01"). Use "Present" for ongoing.

**Bullet rules:**
- Max **4 bullets** per entry.
- Merge `situation` + `task` into first bullet (context).
- Add `action` as second bullet.
- Add `result` as third bullet.
- If result has metrics, append in parentheses: `（Metric: value）`
- If no STAR details, fall back to `highlights` (max 3).

**Skill entries:**
- Format: `**Category** · tag1、tag2、tag3` (Chinese comma `、`)
- No bullets, no date range.

**Contact info:**
- Join phone, email, location with ` | ` (pipe with spaces).
