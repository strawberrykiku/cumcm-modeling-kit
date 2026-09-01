# 可编辑论文项目目录契约

## 目的

项目文件模式把对话中的论文、代码、图表脚本和数据落成一个可检查、可修改、可重新组装的目录。`main.tex` 只是入口文件；正文、程序和绘图脚本都保留为独立源文件。

## 标准目录

```text
solution/
├── main.tex                         # 薄入口：模板导言区 + \input 各分文件
├── paper_content.json               # 内容契约，可选地作为重新生成分文件的来源
├── figure_manifest.json             # 图表 Figure Contract
├── build_report.json                # 最近一次构建、校验和编译状态
├── tex/
│   ├── preamble.tex                 # 从模板提取的导言区
│   └── sections/
│       ├── 01_abstract.tex
│       ├── 02_problem_restatement.tex
│       ├── 03_problem_analysis.tex
│       ├── 04_model_assumptions.tex
│       ├── 05_notation.tex
│       ├── 06_data_processing.tex  # 没有数据处理时可不生成
│       ├── 07_modeling_solution.tex
│       ├── 08_model_validation.tex
│       ├── 09_model_evaluation.tex
│       ├── 10_model_extension.tex  # 没有推广时可不生成
│       ├── 11_ai_statement.tex
│       ├── 12_references.tex
│       └── 13_appendix.tex
├── code/
│   ├── problem1.py                  # 或 .m，按子问题拆分
│   ├── problem2.py
│   ├── run_all.py                   # 如需要
│   └── requirements.txt             # 如需要
├── scripts/
│   └── figures/
│       ├── fig_problem1.py          # 用户题目专用绘图脚本
│       └── ...
├── notes/                            # solver 阶段拆题/文献/选模/结果记录
│   ├── 01_problem_decomposition.md
│   └── ...
├── qa/                               # award-gate 与脚本检查输出（可选）
├── figure_data/                     # JSON/CSV 等可追溯绘图输入
└── figures/                         # 由 figure_pipeline.py 生成的 SVG/PDF/PNG
```

## `paper_content.json` 的分文件字段

保留旧版 `body_tex` 以兼容已有项目；新项目应使用 `sections`。`sections` 的键是语义 ID，构建器负责映射到带编号的 `.tex` 文件：

```json
{
  "title": "论文题目",
  "abstract_tex": "摘要正文（不含文档标记）",
  "keywords": "关键词一；关键词二；关键词三",
  "sections": {
    "problem_restatement": "\\section{问题重述}\\n...",
    "problem_analysis": "\\section{问题分析}\\n...",
    "model_assumptions": "\\section{模型假设}\\n...",
    "notation": "\\section{符号说明}\\n...",
    "data_processing": "\\section{数据处理}\\n...",
    "modeling_solution": "\\section{模型的建立与求解}\\n...",
    "model_validation": "\\section{模型检验}\\n...",
    "model_evaluation": "\\section{模型评价}\\n...",
    "model_extension": "\\section{模型推广}\\n..."
  },
  "ai_statement": "...",
  "bibliography_tex": "\\begin{thebibliography}{99}...",
  "appendix_tex": "...",
  "code_files": [
    {"path": "problem1.py", "content": "# ..."},
    {"path": "problem2.py", "content": "# ..."}
  ],
  "figure_scripts": [
    {"path": "fig_problem1.py", "content": "# ..."}
  ],
  "figure_data_files": [
    {"path": "problem1_results.json", "content": "{...}"}
  ],
  "notes_files": [
    {"path": "01_problem_decomposition.md", "content": "# ..."}
  ]
}
```

每个 section 值必须是可直接被 `\input` 的原始 LaTeX；不要包裹 Markdown 代码围栏。程序和绘图脚本也必须是完整文件内容，不要用省略号代替代码。

## 写入与修改规则

1. 在项目模式下，AI 完成一个论文小节、一个子问题程序或一个绘图脚本后，先写入对应文件，再向用户报告并等待确认。
2. 用户可以直接编辑这些文件；`main.tex` 通过 `\input{tex/sections/...}` 拼接正文，附录可用 `\lstinputlisting{code/problem1.py}` 引用程序。
3. 构建器默认不覆盖已经存在的分文件。若确实要用 JSON 内容覆盖已有文件，显式传 `--overwrite`。
4. 重新运行构建器会重建 `main.tex` 和 `build_report.json`，但不会因为“章节完成”而自动运行；必须由用户或 AI 明确调用命令。
5. 交卷检查阶段可将清单和脚本日志放入 `solution/notes/05_award_gate.md` 与 `solution/qa/`。
6. 所有路径必须是项目目录内的相对路径；禁止 `..`、绝对路径和目录穿越。

## 两种工作模式

- **项目模式（推荐）**：用户提交完整赛题并要求完成解题/论文，或提供项目目录/要求保存文件时，所有新产物写入上述目录，同时在聊天中给出路径和简短摘要。
- **聊天模式**：用户明确要求只看思路/代码块，或只问一个局部问题时，允许只在对话中输出，不创建项目文件。
