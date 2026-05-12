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

### Anti-AI-Trace Writing Rules (CRITICAL)

These rules exist because AI-generated resume bullets are immediately recognizable. Follow them strictly to produce natural, human-readable content.

#### ❌ NEVER do these (classic AI traces):

| Don't | Why it's an AI trace |
|-------|---------------------|
| "深度参与xxx" | 每个 AI 简历都在"深度参与" |
| "聚焦xxx" / "致力于xxx" | 空洞的总结，没人这么写简历 |
| "xxx，验证了xxx方法论" | 应届生简历不会写这种话 |
| "输出xxx报告，为xxx提供核心支撑" | 太模板化 |
| "覆盖xxx全链路" / "完成xxx闭环" | AI 常用词，真人不用 |
| "实践A/B测试优化xxx" | 没细节的 A/B 测试描述是经典 AI 痕迹 |
| bullet 末尾加"（Metric: xxx）"公式化括号 | AI 特有的结构化痕迹 |
| 专业技能写成"AI产品能力 · LLM应用设计" | 分类太 AI，真人写"Python、SQL、Excel" |
| 任何读起来像岗位 JD 的 bullet | 简历 bullet 应该像人说的，不是 HR 写的 |

#### ✅ DO write like a real person:

- **用短句**：一事一行，不要硬凑成三行
- **用具体数字**："5万条数据"比"海量数据"好，"30万字"比"大量内容"好
- **第一人称省略**：直接写"做了xx"，不用"本人""负责"
- **词汇朴素**："做了""搞了""写了""跑了"比"实施""落地""赋能"好
- **适度留白**：不是每个 bullet 都需要"背景-行动-结果"三段式，一段话说清楚一件事就行
