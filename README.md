# Resume Tailor Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

[中文](#中文) | [English](#english)

---

## 中文

**Resume Tailor** 是一个专注于简历定制化的 AI agent skill。输入岗位 JD（文本或截图），自动解析需求、从你的经历库中召回最匹配的经历，生成一份可编辑的 Markdown 简历草稿，经你人工微调后一键导出 PDF。

### 核心原则

- **隐私优先**：你的经历库、手机号、邮箱、JD 截图全部本地私有，不上传任何第三方
- **绝不编造**：每条经历和数字都可追溯到真实条目，`needs_verification` 标记的经历自动排除
- **人工在环**：生成草稿后你必须人工审核修改，再导出 PDF
- **截图降级**：未配置视觉 API 时自动降级为"请粘贴 JD 文本"

### 安装

复制以下指令给你的 LLM agent：

```text
Fetch and follow instructions from:
https://raw.githubusercontent.com/wangzichang224-design/resume-tailor-skill/main/INSTALL.md
```

### 快速开始

1. 按 `INSTALL.md` 完成安装和环境检查
2. 准备好你的经历库（`data/my_experiences.local.json`），参考 `schemas/experience.schema.json` 格式
3. 提出需求，例如：

```text
根据这个JD截图帮我生成一份匹配的简历
```

或者：

```text
tailor my resume for this job: [paste JD text]
```

### 工作流

```
JD (截图/文本) → JD 解析 → 经历召回 → Markdown 简历草稿 → 人工编辑 → PDF 导出
```

### 隐私说明

- 你的真实经历库保存在 `data/my_experiences.local.json`（已被 `.gitignore` 排除）
- 仓库中提供的示例 `examples/sample_experiences.json` 使用虚构候选人
- 视觉 API 调用仅发送 JD 截图，不发送你的经历库
- 运行 `scripts/privacy_check.sh` 可在发布前扫描隐私泄漏

### 依赖

- **必需**：Python >= 3.10
- **可选**：Pandoc + Chrome/Chromium/Edge（PDF 导出）
- **可选**：Claude API / OpenAI API Key（JD 截图自动解析）

---

## English

**Resume Tailor** is an AI agent skill for tailoring your resume to specific job descriptions. Feed it a JD (text or screenshot), and it automatically parses requirements, retrieves the best-matching experiences from your local database, and generates an editable Markdown draft. Fine-tune it manually, then export to PDF.

### Key Principles

- **Privacy first**: your experience database, phone, email, and JD screenshots stay local — nothing is uploaded
- **No fabrication**: every bullet traces to a real experience entry; `needs_verification` entries are auto-excluded
- **Human in the loop**: you review and edit the draft before PDF export
- **Graceful fallback**: if no vision API key is configured, the skill asks you to paste the JD text manually

### Installation

Tell your LLM agent:

```text
Fetch and follow instructions from:
https://raw.githubusercontent.com/wangzichang224-design/resume-tailor-skill/main/INSTALL.md
```

### Quick Start

1. Complete installation via `INSTALL.md`
2. Prepare your experience database at `data/my_experiences.local.json` (see `schemas/experience.schema.json`)
3. Ask naturally:

```text
Tailor my resume for this job: [paste JD text]
```

Or:

```text
Use this JD screenshot to create a matching resume
```

### Privacy

- Real experience data lives in `data/my_experiences.local.json` (gitignored)
- Example data uses a fictional candidate
- Vision API calls send only the screenshot, never your experience database
- Run `scripts/privacy_check.sh` to scan for accidental leaks

### Dependencies

- **Required**: Python >= 3.10
- **Optional**: Pandoc + Chrome/Chromium/Edge (PDF export)
- **Optional**: Claude API / OpenAI API Key (screenshot parsing)

## Repository Structure

```
resume-tailor-skill/
├── SKILL.md                    # Agent behavioral spec
├── INSTALL.md                  # Installation guide
├── README.md                   # This file
├── LICENSE                     # MIT License
├── .env.example                # Vision API key template
├── pyproject.toml              # Python package config
├── data/                       # Private data (gitignored *.local.*)
├── schemas/                    # JSON schemas
│   ├── experience.schema.json
│   ├── jd_analysis.schema.json
│   └── resume_draft.schema.json
├── scripts/
│   ├── resume_tailor/          # Python package
│   │   ├── __init__.py
│   │   ├── jd_parser.py        # Rule-based JD text parser
│   │   ├── jd_image.py         # Vision API screenshot parser
│   │   ├── retriever.py        # 5-dimension experience scoring
│   │   ├── md_generator.py     # Markdown resume renderer
│   │   ├── pipeline.py         # Orchestration + CLI
│   │   └── run_manager.py      # Per-run directory management
│   ├── build_pdf.sh            # Linux/macOS PDF builder
│   ├── build_pdf.ps1           # Windows PDF builder
│   └── privacy_check.sh        # Pre-publish privacy scanner
├── examples/
│   ├── sample_experiences.json # Fictional sample data
│   └── sample_jd.txt           # Sample JD text
└── tests/
```

## License

MIT
