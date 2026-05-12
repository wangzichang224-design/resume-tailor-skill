---
name: resume-review
description: >
  Review the drafted resume for claim accuracy, build a claim-source-map,
  render Markdown to HTML using the selected template, and export the final PDF.
---

# Resume Review

Audit claims, render the resume, and deliver the final PDF.

## Skill Boundary

- **Allowed:** `resume-review` only.
- **Forbidden:** all other skills.

## Workspace Contract

Read from `<workspace>/work/`: `scored-experiences.json`, `draft-resume.md`, `intake-summary.md`, `jd_text.md`
Read templates from the skill assets directory.
Write into `<workspace>/work/`: `claim-source-map.md`
Write into `<workspace>/output/`: `resume.html`, `resume.pdf`

## Review Rules

### Claim-Source-Map Rule
- Every bullet in the draft must be traceable to a source in `experiences.json`.
- If a bullet cannot be traced, flag it as `⚠ No source` — do not silently approve.

### Anti-AI-Trace Review
When reviewing the draft, check specifically for these AI traces and flag them for correction:

- [ ] "深度参与"、"聚焦"、"致力于"、"赋能"、"闭环"、"方法论"、"抓手"、"落地" 等空洞词汇
- [ ] 专业技能写成"AI产品能力 · LLM应用设计"这类分类式写法（应改为"Python、SQL、Excel"）
- [ ] Bullet 末尾有公式化的（Metric: value）括号
- [ ] 每个 bullet 都硬套"背景-行动-结果"三段式，没有省略
- [ ] 任何读起来像 JD 描述的句子
- [ ] 过于正式的措辞（真人简历用词更随意）

If any of these are found, go back to resume-drafting for corrections before proceeding.

## Template Resolution

Templates are located at:
- Primary: `~/.claude/skills/resume-review/assets/resume-template/style.css` and `template.html`
- For additional templates (optional): `~/.claude/skills/resume-review/templates/`

**Default template:** `assets/resume-template/` — 双栏带照片布局（左侧深蓝底+照片+联系方式+技能，右侧正文）。照片路径来自 `data/my_experiences.local.json` 中的 `personal_info.photo` 字段。如果用户资料库中没有照片，使用 `assets/photo.png` 作为默认照片。

**Other templates (optional):**
- `templates/zh/standard/` — 中文标准单栏布局
- `templates/industry/ats/` — 英文ATS单栏布局

**Template selection logic:**
- Default: use `assets/resume-template/` (带照片双栏模板)
- Chinese JD → `templates/zh/standard/` (or fallback to generic)
- English JD → `templates/industry/ats/` (or fallback to generic)
- User can specify: "用英文模板" or keep default

If the specific template directory doesn't exist, use the generic `assets/resume-template/`.

## Step 1. Build Claim-Source-Map

Create `work/claim-source-map.md` — a table tracing every claim in the draft back to its source:

```markdown
# Claim-Source Map

| # | Section | Claim | Source Entry | Evidence Level | Status |
|---|---------|-------|-------------|----------------|--------|
| 1 | 教育 | GPA 3.66/4 | exp_edu_shisu | verified | ✓ Confirmed |
| 2 | 项目经历 | 效率提升80% | exp_project_ai_agent | verified | ✓ Confirmed |
| 3 | 实习经历 | 处理5万条数据 | exp_intern_fuji | plausible | ? Verify |
```

Rules:
- Every bullet point in the draft must have a corresponding row.
- `Status` is `✓ Confirmed` if data comes from a `verified` source, `? Verify` if `plausible`, `⚠ Needs check` if `anecdotal`.
- If the user needs to verify a `?` or `⚠` item, ask them before proceeding.

## Step 2. Confirm Uncertain Claims

Present the `? Verify` and `⚠ Needs check` items to the user:
- "这个项目写的内容根据的是 anecdotal 级别的信息，你能确认数据的准确性吗？"
- "如果没问题，我就直接用。如果你有更精确的数据可以替换。"

**If the user confirms → proceed. If they provide corrections → update both the draft and the claim-source-map.**

## Step 3. Convert Markdown to HTML

Read `work/draft-resume.md` and convert to HTML using these rules:

| Markdown | HTML |
|----------|------|
| `# Title` | `<h1>Title</h1>` |
| `## Title` | `<h2>Title</h2>` |
| `- text` | `<li>text</li>` inside `<ul>` |
| `**text**` | `<strong>text</strong>` |
| `text1 · text2` | `<span class="date-sep">text1 · text2</span>` |
| `---` | `<hr>` |
| `text1 | text2` (contact) | `<span class="contact-item">text1 | text2</span>` |
| empty line between entries | close/open `</ul><ul>` |

## Step 4. Read and Apply Template

Read `template.html` and `style.css` from the template directory.

In `template.html`, substitute:
- `{{CSS}}` → the full content of `style.css`
- `{{PHOTO}}` → photo file path (from `data/my_experiences.local.json` → `personal_info.photo`, or default `assets/photo.png`)
- `{{NAME}}` → user's name
- `{{TITLE}}` → job title from JD analysis
- `{{PHONE}}` → user's phone number
- `{{EMAIL}}` → user's email
- `{{LOCATION}}` → user's location
- `{{SKILLS}}` → skill tags as HTML (`<span class="skill-tag">Python</span>`)
- `{{CONTENT}}` → the HTML body generated in Step 3

## Step 5. Export PDF

Try weasyprint first:
```bash
python3 -c "
import weasyprint
html_content = open('/tmp/resume.html', encoding='utf-8').read()
weasyprint.HTML(string=html_content).write_pdf('<workspace>/output/resume.pdf')
"
```

If weasyprint is available → save to `output/resume.pdf`.

If not available → save `output/resume.html` and tell the user:
> "weasyprint 没安装，已生成 HTML 文件。`pip install weasyprint` 安装后重试，或直接在浏览器打开 HTML 用打印→另存为 PDF."

## Step 6. Report

Report final output paths:
- `output/resume.pdf` (or `output/resume.html` if weasyprint unavailable)
- `output/resume.html` (always generated for reference)
- `work/claim-source-map.md` (claim traceability)
