# CUMCM 图表生成流水线

这是 `math-modeling-solver → math-modeling-paper → cumcm-award-gate` 之间的可执行图表阶段。它不改变三段式主流程，只在论文写作和最终质检之间增加可追溯的图表产物。项目文件模式下，题目专用绘图代码必须保存在 `solution/scripts/figures/`，不能只打印在对话中。

## 输入

- solver 的模型输出、结果表和中间数据；
- 论文草稿中的 Figure Contract；
- `figure_manifest.json`；
- `figure_data/` 中的 JSON/CSV 数据。
- `scripts/figures/` 中的题目专用绘图脚本。

## 执行

1. 从每个子问题的结论反推需要的证据图；没有独立结论的图不生成。
2. 选择图类型：定量图用 Python/Matplotlib、MATLAB 或 R；概念图用 SVG/PDF；非定量插画才允许调用 imagegen。
3. 先将每张图的绘图源代码保存到 `scripts/figures/`，将输入数据保存到 `figure_data/`；再运行：

   ```bash
   # 从仓库根目录执行；所有产物仍写入 solution/ 项目目录
   python skills/math-modeling-paper/scripts/figure_pipeline.py \
     --manifest solution/figure_manifest.json \
     --out-dir solution/figures \
     --formats svg,pdf,png
   ```

4. 检查 `figures/figure_manifest.generated.json`，确认每张图都记录了文件和 SHA-256；生成器只读取 manifest/data，不会擅自执行用户绘图脚本，因此需要时先手工运行或由 AI 明确调用这些脚本。
5. 在 `main.tex` 中为每张图添加 `figure` 环境、描述性 `caption`、唯一 `label` 和 `\includegraphics`；正文必须有交叉引用和解释段。
6. 使用 `cumcm-award-gate` 检查最终 PDF：图片路径、字体、图题、坐标轴、单位、黑白可辨识性和裁切。

## 失败处理

- 没有 matplotlib：提示安装依赖，不能静默跳过定量图；
- 缺少源数据：报告缺失字段和对应 Figure Contract，不能填入虚构数据；
- 缺少 diagram/imagegen 能力：使用脚本的 `flowchart` 或 Matplotlib patches 作为确定性后备；
- XeLaTeX 找不到图片：修正相对路径或复制资源后重新编译；
- 图片只具有装饰性：从论文中移除，而不是强行保留。

## 最终产物

```text
figure_manifest.json
figure_data/
scripts/figures/*.py
figures/*.svg
figures/*.pdf
figures/*.png
main.tex  # 引用实际 figures 文件
```
