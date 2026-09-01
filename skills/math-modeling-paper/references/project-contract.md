# 一键论文构建契约

`build_cumcm_project.py` 负责“已有建模内容 → 论文项目”的确定性构建。它不替代 solver，也不生成未经验证的模型结论。

## 必需输入：`paper_content.json`

字段的机器可读 schema 见 `templates/cumcm-latex/paper_content.schema.json`。

```json
{
  "title": "基于几何可见性与差分进化的烟幕投放策略",
  "abstract_tex": "本文……问题一得到……问题二得到……",
  "keywords": "烟幕干扰；轨迹优化；线段—球判定；差分进化",
  "body_tex": "\\section{问题重述}\\n……\\n\\section{模型建立与求解}\\n……",
  "ai_statement": "本参赛队使用 AI 工具辅助文字整理和代码检查，模型、数据和结论由参赛队独立核验。",
  "bibliography_tex": "\\begin{thebibliography}{99}\\bibitem{ref1} ...\\end{thebibliography}",
  "appendix_tex": "\\subsection*{附录 A\\quad 支撑材料}\\n……"
}
```

字段说明：

- `title`、`abstract_tex`、`keywords`、`body_tex` 必须是非空字符串；
- `abstract_tex`、`body_tex`、`bibliography_tex`、`appendix_tex` 是原始 LaTeX，不要再包裹 Markdown 代码围栏；
- `body_tex` 应包含从 `\\section{问题重述}` 开始的正文，不要包含 `\\documentclass`、`\\begin{document}` 或 `\\end{document}`；
- `ai_statement` 必须放在参考文献之前；
- 正文图像统一写成 `\\includegraphics[width=...]{figures/figure_id.pdf}`，文件由 figure pipeline 生成。

## 可选输入：`figure_manifest.json`

格式见 `figure-generation.md`。它必须含有真实数据、Figure Contract 和图题。构建器默认发现 `project/figure_manifest.json`；也可以用 `--manifest` 显式指定。

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

`--compile` 会在检测到 XeLaTeX 时编译两遍；没有 XeLaTeX 时不会失败，而是在 `build_report.json` 中说明应使用 Overleaf XeLaTeX。构建器始终生成：

```text
solution/main.tex
solution/build_report.json
solution/figures/
solution/figures/figure_manifest.generated.json  # 有 manifest 时
solution/xelatex-pass-1.log / xelatex-pass-2.log # 编译时
```

## 构建器的硬性检查

- 拒绝 `XXX`、`……`、`此处插图`、`待补`、`TODO` 等占位符；
- 拒绝缺失的 `\\includegraphics` 文件；
- 拒绝重复或缺失的论文必需字段；
- 正文必须有且只有一对 `\\begin{document}` / `\\end{document}`；
- 图表数据、正文、Excel 和代码应在构建前由作者核对，构建器只负责路径和结构一致性。
