# 图表生成与论文插图工作流

本文件把“图表规范”扩展为可执行的“数据/结论 → 图 → LaTeX 插图”流程。图表不是装饰：每张图必须服务于一个可验证的结论，并且必须能够从题目数据、模型输出或可追溯的中间结果重新生成。

## 1. Figure Contract：画图前先写清楚证据链

每张图在生成前建立一个条目，至少包含：

```json
{
  "id": "fig_trajectory",
  "claim": "最优策略使烟幕云团在导弹—目标视线束附近形成连续遮蔽",
  "evidence": ["model_output.strategy", "model_output.m1_trajectory"],
  "type": "trajectory_3d",
  "section": "问题四模型结果",
  "caption": "图 4  三架无人机与导弹、烟幕云团的三维轨迹",
  "source": "artifacts/figure_data/trajectory.json",
  "outputs": ["svg", "pdf", "png"]
}
```

要求：

- `claim` 必须是一句话结论，而不是“展示某某数据”；
- `evidence` 必须能回溯到题目数据、代码输出或结果表；
- 没有独立证据的 panel 删除，不为填版面增加图；
- `caption` 必须说明对象、条件和比较关系；
- 生成后在正文中解释“图中发现了什么、为什么、对问题意味着什么”。

## 2. 图类型与工具路由

### 2.1 定量数据图（默认路径）

必须使用真实数据，由 Python/Matplotlib、MATLAB 或 R 生成；禁止用图像生成模型伪造数值、曲线、坐标轴或实验结果。常用类型：

| 论文证据 | 推荐图 |
|---|---|
| 时间序列、遮蔽区间、事件顺序 | 折线图、区间时间轴 |
| 预测值与真实值、误差 | 散点图、残差图 |
| 参数扫描、灵敏度 | 灵敏度曲线、龙卷风图 |
| 类别/方案比较 | 排序柱状图、箱线图 |
| 优化迭代过程 | 收敛曲线、Pareto 图 |
| 空间运动/几何关系 | 二维或三维轨迹图 |

### 2.2 概念图、流程图和几何示意图

- 优先输出 SVG/PDF 矢量图；
- 有 `baoyu-diagram` 或其他 diagram skill 时，可调用它生成结构图；
- 没有 diagram skill 时，使用 Matplotlib patches、Graphviz、TikZ 或 Mermaid 转 SVG；
- 概念图中的数值、箭头方向、变量名称必须和模型一致；
- 不要把 AI 生成的艺术图片当成定量证据。

### 2.3 可选的 AI 生成插图

仅当用户明确要求封面、背景、非定量概念插画，或插图能显著帮助解释场景时，才调用 `imagegen`/`baoyu-image-gen` 等图像 skill。必须：

- 标记为“示意图”而非实验结果；
- 不生成、修改或猜测数据图表；
- 保存提示词、参考图来源和生成日期；
- 在论文中避免使用会泄露身份或制造事实的画面。

## 3. 标准产物目录

论文项目中统一使用：

```text
solution/
├── figures/                 # 最终插图：SVG + PDF + PNG
├── figure_data/             # 可追溯的 JSON/CSV 中间数据
├── figure_manifest.json     # 每张图的 Figure Contract
└── scripts/                 # 生成图的可运行脚本
```

在项目文件模式下，题目专用绘图源码统一保存到 `scripts/figures/`，图表输入数据统一保存到 `figure_data/`；不要只把绘图代码留在聊天代码块中。仓库提供的 `figure_pipeline.py` 是生成器，不会监控目录，也不会擅自执行用户保存的绘图脚本。

如果用户已有项目结构，保持其结构，只需建立等价映射。最终 `.tex` 中的 `\includegraphics` 必须引用实际存在的 `figures/` 文件。

## 4. 可执行生成器

仓库提供 `scripts/figure_pipeline.py`，用于生成常见的论文图。它读取 JSON manifest，并默认同时输出 SVG、PDF 和 600 dpi PNG：

```bash
python scripts/figure_pipeline.py \
  --manifest figure_manifest.json \
  --out-dir figures \
  --formats svg,pdf,png
```

支持的 `type`：

- `line`：一条或多条折线；
- `scatter`：散点及可选拟合线；
- `bar`：排序/比较柱状图；
- `sensitivity`：基准值及参数扰动曲线；
- `interval`：有效区间时间轴；
- `trajectory_3d`：三维轨迹；
- `flowchart`：分层流程图。

数据可以写在 manifest 的 `data` 字段中，也可以由 `source` 指向 JSON 文件。生成器不允许缺少数据或图题；对于定量图，输入数据长度不一致会直接报错。轴标签、`evidence` 和 `section` 仍须由作者在 manifest 和代码审查中确认。

## 5. 论文插图映射

生成后建立 `id → filename → section → claim` 映射。LaTeX 使用：

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.92\textwidth]{figures/fig_trajectory.pdf}
  \caption{三架无人机与导弹、烟幕云团的三维轨迹}
  \label{fig:trajectory}
\end{figure}
```

正文必须出现 `图~\ref{fig:trajectory}`，并紧跟解释段。表题在表上方，图题在图下方；坐标轴写变量名和单位；黑白打印仍应能通过线型、标记或明度区分数据。

## 6. 生成后的检查

交付前逐项确认：

- manifest 中每张图都有 `claim`、`evidence`、`caption` 和输出文件；
- 所有 `\includegraphics` 路径存在；
- SVG/PDF/PNG 三种格式来自同一份数据；
- 没有默认标题、空图、截断坐标轴、乱码、图例遮挡或单位缺失；
- 图中数字与论文正文、Excel 和代码输出一致；
- `cumcm-award-gate` 的图表检查脚本能够读取最终 PDF；
- 图表只是辅助证据，不替代公式、表格和文字论证。
