# Resume Tailor Skill

<div align="center">

## 简历定制 Skill

---

把一张岗位截图（或一段 JD 文本）变成一份匹配该岗位的精美 PDF 简历。
**隐私优先**：你的经历数据永远在本地。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[中文](#中文) | [English](#english)

---

</div>

## 中文

### 这是什么

**Resume Tailor** 是一个 4-skill 简历定制流水线，专为 Claude Code / OpenClaw 设计。

### 工作流程

```
JD（截图/文本）
  │
  ├─ [resume-jd-intake]  读取 JD + 加载简历库 → 确认不确定的信息
  │
  ├─ [resume-drafting]    JD 分析 → 5 维评分 → 排序 → 写 Markdown 简历
  │
  └─ [resume-review]     Claim 追溯审核 → HTML 渲染 → PDF 导出
```

### v2.0 新特性

- **4-skill 架构**：编排 / 采集 / 写作 / 审核，职责清晰
- **Claim-Source-Map**：每个 bullet 都有来源追溯，杜绝幻觉
- **信息确认机制**：不确定的信息先问你，不脑补填充
- **多模板支持**：中文标准 / 英文 ATS / 学术简历，按需选择
- **精致排版**：升级 CSS，A4 专业布局，可直接投递

### 安装

#### Claude Code（推荐）

```bash
# 1. 创建 skills 目录
mkdir -p ~/.claude/skills/resume-tailor \
         ~/.claude/skills/resume-jd-intake \
         ~/.claude/skills/resume-drafting \
         ~/.claude/skills/resume-review

# 2. 复制 skill 文件
cp skills/resume-tailor/SKILL.md     ~/.claude/skills/resume-tailor/
cp skills/resume-jd-intake/SKILL.md  ~/.claude/skills/resume-jd-intake/
cp skills/resume-drafting/SKILL.md   ~/.claude/skills/resume-drafting/
cp skills/resume-review/SKILL.md     ~/.claude/skills/resume-review/

# 3. 复制模板和资源
cp -r assets ~/.claude/skills/resume-review/
cp -r templates ~/.claude/skills/resume-review/

# 4. 准备简历库
# 在项目目录 data/my_experiences.local.json 放置你的经历数据
```

#### OpenClaw / 微信机器人

参考 `INSTALL.md` 中的 Python pipeline 安装方式。

### 使用

在 Claude Code 中：

```
帮我根据这个 JD 截图定制简历，用中文标准模板
```

或者：

```
tailor my resume for this job, use the English ATS template
```

### 简历库格式

`data/my_experiences.local.json` 是一个 JSON 数组，每条经历的格式：

```json
{
  "id": "exp_intern_fuji",
  "category": "internship",
  "title": "富士（中国）投资有限公司",
  "subtitle": "活动运营",
  "date_start": "2025-10",
  "date_end": "2026-01",
  "tags": ["数据运营", "AI产品", "活动运营"],
  "star_details": {
    "situation": "集团多业务线数据庞大，日常流程耗时较长",
    "task": "需要提升效率",
    "action": "搭建 AI 简历初筛模型，重构费用管理 SOP",
    "result": "简历初筛效率提升50%，流程审批效率提升30%"
  },
  "evidence_level": "verified",
  "needs_verification": false,
  "target_roles": ["AI产品经理", "产品经理"],
  "metrics": [
    {"metric": "效率提升", "value": "50%", "verified": true}
  ]
}
```

完整字段说明见 `schemas/experience.schema.json`。

### 模板

| 模板 | 路径 | 适用场景 |
|------|------|---------|
| 通用 | `assets/resume-template/` | 默认，简洁单栏 |
| 中文标准 | `templates/zh/standard/` | 中文求职，商务风格 |
| 英文 ATS | `templates/industry/ats/` | 外企求职，ATS 友好 |
| 学术简历 | `templates/research/ats/` | 学术/研究岗位 |

---

## English

### What is this

**Resume Tailor** is a 4-skill pipeline that turns a job description (screenshot or text) into a polished PDF resume tailored to the JD.

### Installation

```bash
# Create skill directories
mkdir -p ~/.claude/skills/resume-tailor \
         ~/.claude/skills/resume-jd-intake \
         ~/.claude/skills/resume-drafting \
         ~/.claude/skills/resume-review

# Copy skill files
cp skills/resume-tailor/SKILL.md     ~/.claude/skills/resume-tailor/
cp skills/resume-jd-intake/SKILL.md  ~/.claude/skills/resume-jd-intake/
cp skills/resume-drafting/SKILL.md   ~/.claude/skills/resume-drafting/
cp skills/resume-review/SKILL.md     ~/.claude/skills/resume-review/

# Copy assets and templates
cp -r assets ~/.claude/skills/resume-review/
cp -r templates ~/.claude/skills/resume-review/
```

### Quick Start

1. Prepare `data/my_experiences.local.json`
2. In Claude Code: "tailor my resume for this job description"

### Templates

| Template | Path | Use Case |
|----------|------|----------|
| Generic | `assets/resume-template/` | Default, clean single-column |
| Chinese | `templates/zh/standard/` | Chinese job applications |
| English ATS | `templates/industry/ats/` | Foreign companies, ATS-friendly |
| Academic | `templates/research/ats/` | Research/academic positions |

### License

MIT
