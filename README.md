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

Claude Code 只扫描 `~/.claude/skills/<name>/SKILL.md`（一层目录）。把三个 skill 目录放进去：

```bash
git clone https://github.com/strawberrykiku/cumcm-modeling-kit.git /tmp/cumcm-kit
cp -r /tmp/cumcm-kit/skills/math-modeling-solver ~/.claude/skills/
cp -r /tmp/cumcm-kit/skills/math-modeling-paper  ~/.claude/skills/
cp -r /tmp/cumcm-kit/skills/cumcm-award-gate     ~/.claude/skills/
```

（可选）把 `workflows/cumcm-pipeline.md` 放到项目里或 `~/.claude/workflows/` 作为流程参考。

重启 Claude Code，三个 skill 会按各自 description 在合适的时候自动加载。

## 怎么用

拿到赛题后直接粘贴/描述题目，Claude 会按三段式接力：

```
math-modeling-solver（解题）→ math-modeling-paper（写作）→ cumcm-award-gate（交卷前把关）
```

详见 `workflows/cumcm-pipeline.md`。三个贯穿始终的"够国一"要求：**每问必有一数、创新账本、每问都有检验**。

## 依赖

- 核心内容（solver / paper / 自查清单）：无额外依赖，Claude Code 自带工具即可。
- `cumcm-award-gate` 的可选脚本：`figqa.py` 需要 `matplotlib`；`pdf_qa.sh` 需要 `poppler-utils`。没装不影响自查清单本身，脚本会提示怎么装。

## 致谢与许可

本仓库是对两个 MIT 开源项目的组合与再创作，向原作者致谢：

- [Lupynow/math-modeling-skills](https://github.com/Lupynow/math-modeling-skills) —— `math-modeling-solver` 与 `math-modeling-paper` 原样收录（MIT）。
- [sweetcornna/mathodology](https://github.com/sweetcornna/mathodology) —— `cumcm-award-gate` 的质控关卡思路，以及 `figqa.py` / `pdf_qa.sh` 两个脚本，提炼/收录自此项目（MIT）。

各来源的许可与详细归属见 `NOTICE.md`。本仓库整体以 MIT 许可发布，见 `LICENSE`。

## 设计取舍（为什么是轻壳）

- **重壳**（mathodology 原版）：9 阶段多 agent + 结构化交接 + 三席盲评 + 强制门禁。质量兜底强，但 token/时间成本高、零件多、易中途卡壳。
- **轻壳**（本组合）：单上下文，保留内容核 + 自查清单 + 盲评自评。国赛 72 小时、有队友能互审时，把时间花在内容上更划算；独立批判用"新对话盲评"低成本补位。
- 什么时候该上重壳：打美赛、没有靠谱队友互审、或要把 skill 做成给很多人用的产品。
