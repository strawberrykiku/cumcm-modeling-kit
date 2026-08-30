# CUMCM Modeling Kit · 国赛数学建模三段式 Skill

> 从拿到赛题到交出论文的一条龙 Claude Code skill 组合，为**国赛新手**优化：解题 → 写作 → 交卷前把关。

一句话：把两套优秀的开源 skill 的长处合成一个——用 [Lupynow/math-modeling-skills](https://github.com/Lupynow/math-modeling-skills) 的**内容核**（方法库、代码库、写作红线），套上从 [sweetcornna/mathodology](https://github.com/sweetcornna/mathodology) 提炼的**轻量质控关卡**（交卷前自查、盲评自评、图表/PDF 检查）。不上多 agent，一个对话、一个人就能跑完。

## 为什么是这三个 skill

外壳不产生质量，只拦住质量的漏洞；真正的分靠内容。所以本组合以内容为主、质控为辅：

| Skill | 来源 | 作用 |
|---|---|---|
| `math-modeling-solver` | Lupynow（原样收录） | 解题：12 类题型判定、95+ 模型决策矩阵、8 本 cookbook、12 本 playbook、29 个代码模板 |
| `math-modeling-paper` | Lupynow（原样收录） | 写作：国赛/美赛双赛道结构、摘要、模型检验、四轮自审、去 AI 味 |
| `cumcm-award-gate` | 本仓库新增（提炼自 mathodology） | 把关：交卷前强制自查清单 + 创新账本/稳健性 + 盲评自评 + figqa/pdf_qa 脚本 |

为什么选"轻壳 + 强制自查清单"这个组合，取舍分析见文末。

## 目录结构

```
cumcm-modeling-kit/
├── skills/
│   ├── math-modeling-solver/     # 内容核 · 解题（来自 Lupynow）
│   ├── math-modeling-paper/      # 内容核 · 写作（来自 Lupynow）
│   └── cumcm-award-gate/         # 新增 · 交卷前把关
│       ├── SKILL.md
│       └── scripts/              # figqa.py + pdf_qa.sh（来自 mathodology）
└── workflows/
    └── cumcm-pipeline.md         # 三段式流程编排
```

## 安装

> ⚠️ **不能把整个仓库直接 clone 进 skills 目录。** Claude Code 只认 `~/.claude/skills/<名字>/SKILL.md` 这一层；本仓库把三个 skill 包在 `skills/` 下，安装时要把 `skills/` 下的**三个子目录**拷进去。**三个必须一起装**——solver 会读 paper 的文献文件，gate 是第三关。

**Windows（PowerShell）**

```powershell
git clone https://github.com/strawberrykiku/cumcm-modeling-kit.git "$env:TEMP\cumcm-kit"
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
Copy-Item -Recurse -Force "$env:TEMP\cumcm-kit\skills\*" "$env:USERPROFILE\.claude\skills\"
```

**macOS / Linux（bash）**

```bash
git clone https://github.com/strawberrykiku/cumcm-modeling-kit.git /tmp/cumcm-kit
mkdir -p ~/.claude/skills
cp -r /tmp/cumcm-kit/skills/* ~/.claude/skills/
```

**备选：npx**（目录结构与 Lupynow 原版一致，理论可用；未实测，装完确认三个都在）

```bash
npx skills add strawberrykiku/cumcm-modeling-kit --skill '*'
```

装完**重启 Claude Code**。验证三个 skill 到位（应看到 `math-modeling-solver` / `math-modeling-paper` / `cumcm-award-gate`）：Windows 用 `ls $env:USERPROFILE\.claude\skills`，macOS/Linux 用 `ls ~/.claude/skills`。

**依赖**：核心内容（solver / paper / 自查清单）无需额外依赖。`cumcm-award-gate` 的可选脚本 `figqa.py` 需要 `matplotlib`、`pdf_qa.sh` 需要 `poppler-utils`；不装不影响自查清单本身，脚本会提示怎么装。

## 怎么用

### 是不是丢给它题目就行？

大致是——但它是**分步陪跑的助手，不是一键出论文的机器**。

1. 直接**粘贴赛题文本**，`math-modeling-solver` 通常会自动触发；没触发就明说："用 math-modeling-solver 解这道题"。
2. 它先确认：**国赛还是美赛、偏好 Python 还是 MATLAB**。
3. 之后**分阶段走、每阶段停下等你确认**（可纠偏、可回退）：

```
拆题 → (查文献，可跳过) → 选模型（给你多个候选让你拍板）→ 出代码 → 论文草稿片段 [PAPER_READY]
```

4. 说"开始写论文" → 接力到 `math-modeling-paper`，逐章写（摘要 / 问题分析 / 建模求解 / 检验 / 评价……），并做四轮自审 + 去 AI 味。
5. 说"过一遍交卷清单" → 接力到 `cumcm-award-gate`，跑 A–H 强制自查 + 图表/PDF 检查 + 对照国一标准的盲评自评打分。

完整流程和 72 小时时间盒见 `workflows/cumcm-pipeline.md`。贯穿始终的三个"够国一"要求：**每问必有一数、创新账本、每问都有检验**。

### 你会得到什么

- 结构化拆题、（可选）文献摘要、带理由和候选的模型推荐
- 公式推导 + 伪代码 + **可运行的 Python/MATLAB 代码**（Claude Code 装了解释器就能真跑出数值和图）
- 论文各章草稿正文 + 附录代码
- 一份过完的交卷自查清单 + 图表缺陷/PDF 匿名性检查 + 一个国一标准下的自评分数

### 它不会替你做的

- **不会一键生成排版好、能直接交的成品 PDF**——最后的 LaTeX/Word 组装和编译要你（在它帮助下）完成。
- 替不了你理解：评审会查代码与论文一致性、也看 AI 痕迹，比赛是你自己的作品。它加速你、兜住漏洞，但你得看懂并对交出去的东西负责。

## 致谢与许可

本仓库是对两个 MIT 开源项目的组合与再创作，向原作者致谢：

- [Lupynow/math-modeling-skills](https://github.com/Lupynow/math-modeling-skills) —— `math-modeling-solver` 与 `math-modeling-paper` 原样收录（MIT）。
- [sweetcornna/mathodology](https://github.com/sweetcornna/mathodology) —— `cumcm-award-gate` 的质控关卡思路，以及 `figqa.py` / `pdf_qa.sh` 两个脚本，提炼/收录自此项目（MIT）。

各来源的许可与详细归属见 `NOTICE.md`。本仓库整体以 MIT 许可发布，见 `LICENSE`。

## 设计取舍（为什么是轻壳）

- **重壳**（mathodology 原版）：9 阶段多 agent + 结构化交接 + 三席盲评 + 强制门禁。质量兜底强，但 token/时间成本高、零件多、易中途卡壳。
- **轻壳**（本组合）：单上下文，保留内容核 + 自查清单 + 盲评自评。国赛 72 小时、有队友能互审时，把时间花在内容上更划算；独立批判用"新对话盲评"低成本补位。
- 什么时候该上重壳：打美赛、没有靠谱队友互审、或要把 skill 做成给很多人用的产品。
