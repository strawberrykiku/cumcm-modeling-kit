# 归属与许可说明（NOTICE）

本仓库 **CUMCM Modeling Kit** 是对两个 MIT 开源项目的组合与再创作。以下说明每个组成部分的来源与许可，感谢原作者的工作。

## 组成部分与来源

| 路径 | 来源 | 许可 |
|---|---|---|
| `skills/math-modeling-solver/` | [Lupynow/math-modeling-skills](https://github.com/Lupynow/math-modeling-skills) 原样收录 | MIT（见该目录内 `LICENSE`） |
| `skills/math-modeling-paper/` | [Lupynow/math-modeling-skills](https://github.com/Lupynow/math-modeling-skills) 原样收录 | MIT（见该目录内 `LICENSE`） |
| `skills/cumcm-award-gate/scripts/figqa.py` | [sweetcornna/mathodology](https://github.com/sweetcornna/mathodology) 收录 | MIT |
| `skills/cumcm-award-gate/scripts/pdf_qa.sh` | [sweetcornna/mathodology](https://github.com/sweetcornna/mathodology) 收录 | MIT |
| `skills/cumcm-award-gate/SKILL.md` | 本仓库原创（质控关卡的清单与协议，思路提炼自 mathodology 的 award-gates 与 modeler） | MIT |
| `workflows/cumcm-pipeline.md`、`README.md`、本文件 | 本仓库原创 | MIT |

## 上游许可原文

### Lupynow/math-modeling-skills

```
MIT License

Copyright (c) 2026 Lupynow
```

完整许可文本随 `skills/math-modeling-solver/LICENSE` 与 `skills/math-modeling-paper/LICENSE` 一并保留在本仓库内。

### sweetcornna/mathodology

```
MIT License

Copyright (c) 2026 Mathodology contributors
```

`figqa.py` 与 `pdf_qa.sh` 收录自该项目；其许可与本仓库根目录 `LICENSE` 中列出的版权声明一并适用。

## 改动说明

- Lupynow 的两个 skill（`math-modeling-solver`、`math-modeling-paper`）**未做修改**，原样收录，以便随上游更新。
- `cumcm-award-gate` 为本仓库新增：SKILL.md 系原创内容；`scripts/` 下两个脚本收录自 mathodology，未做修改。
- 本组合的设计取舍（"轻壳 + 强制自查清单"）说明见 `README.md`。
