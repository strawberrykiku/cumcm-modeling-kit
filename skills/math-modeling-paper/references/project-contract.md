# 可编辑论文项目构建契约

`build_cumcm_project.py` 负责把已经核验的论文、代码、图表脚本和数据写入一个可编辑项目，并生成一个由 `\input` 组成的 `main.tex`。它不替代 solver，也不生成未经验证的模型结论。

## 标准项目布局

```text
solution/
├── main.tex
├── paper_content.json
├── figure_manifest.json
├── build_report.json
├── tex/preamble.tex
├── tex/sections/*.tex
├── code/*.{py,m,r,...}
├── scripts/figures/*.py
├── notes/*.md
├── qa/                              # 可选的质检日志
├── figure_data/*.{json,csv}
└── figures/*.{svg,pdf,png}
```

详细文件命名和编辑规则见 `project-layout.md`。

## `paper_content.json`

必需字段：

```json
{
  "title": "基于几何可见性与差分进化的烟幕投放策略",
  "abstract_tex": "本文……",
  "keywords": "烟幕干扰；轨迹优化；稳健性"
}
```

新项目应使用 `sections` 将正文拆分：

```json
{
  "sections": {
    "problem_restatement": "\\section{问题重述}\\n……",
    "problem_analysis": "\\section{问题分析}\\n……",
    "model_assumptions": "\\section{模型假设}\\n……",
    "notation": "\\section{符号说明}\\n……",
    "data_processing": "\\section{数据处理}\\n……",
    "modeling_solution": "\\section{模型的建立与求解}\\n……",
    "model_validation": "\\section{模型检验}\\n……",
    "model_evaluation": "\\section{模型评价}\\n……",
    "model_extension": "\\section{模型推广}\\n……"
  },
  "ai_statement": "本参赛队……",
  "bibliography_tex": "\\begin{thebibliography}{99}...",
  "appendix_tex": "...",
  "code_files": [
    {"path": "problem1.py", "content": "# 完整程序"},
    {"path": "problem2.py", "content": "# 完整程序"}
  ],
  "figure_scripts": [
    {"path": "fig_problem1.py", "content": "# 完整绘图程序"}
  ],
  "figure_data_files": [
    {"path": "problem1_results.json", "content": "{...}"}
  ],
  "notes_files": [
    {"path": "01_problem_decomposition.md", "content": "# 拆题记录"}
  ]
}
```

每个 section、程序和脚本都必须是完整的原始文本，不要包裹 Markdown 围栏。`body_tex` 仍被接受，作为旧项目兼容字段；没有 `sections` 时会写成 `tex/sections/02_body_legacy.tex`，并在报告中标记 `legacy_body_fallback: true`。

## 构建命令

从仓库根目录运行：

```bash
python skills/math-modeling-paper/scripts/build_cumcm_project.py \
  --project ./solution \
  --content ./paper_content.json \
  --template ./templates/cumcm-latex/main.tex \
  --manifest ./figure_manifest.json \
  --formats svg,pdf,png \
  --compile
```

如果图表 manifest 已放在 `solution/figure_manifest.json`，可以省略 `--manifest`。外部传入的 manifest 会复制一份到项目根目录；为保证之后可独立重建，manifest 中的 `source` 建议使用相对于项目根目录的路径（如 `figure_data/problem1.json`）。图表生成使用真实数据；用户提供的 `scripts/figures/*.py` 会被保存，但不会被构建器擅自执行。

## 覆盖策略

- `main.tex` 和 `build_report.json` 是派生文件，每次构建都会重写。
- `tex/preamble.tex`、各 section、`code/`、`scripts/figures/` 和 `figure_data/` 中已经存在的文件默认保留，避免覆盖用户修改。
- 需要从 JSON 重新生成这些文件时，显式增加 `--overwrite`。
- 路径必须是项目内相对路径；构建器拒绝绝对路径、`..` 和空路径。

## 构建器检查范围

构建器会检查：

- `main.tex` 中只有一对 `\begin{document}` / `\end{document}`；
- section 文件和 `\input` 路径存在；
- LaTeX 中的占位符（`XXX`、`……`、`此处插图`、`待补`、`TODO`、`PLACEHOLDER`）已清理；
- `\includegraphics` 引用的图片存在；
- 图表脚本、PDF 匿名性和数学结果的一致性仍需单独运行相应脚本并由作者核验。

有 XeLaTeX 时 `--compile` 会编译两遍；没有 XeLaTeX 时构建仍可生成源文件，但报告会标注需要使用 Overleaf XeLaTeX。
