# 国赛 LaTeX 论文模板（匿名版）

配合 `math-modeling-paper` skill 用：把 skill 生成的各章内容填进 `main.tex`，编译成可提交的 PDF。

## 用什么编译

- 必须用 **XeLaTeX**（含中文，`ctexart` 需要它）。命令：`xelatex main.tex`，**连编两次**（生成目录、交叉引用、页码）。
- 需要一个完整 TeX 发行版：
  - 本地：**TeX Live**（完整安装）或 Windows 的 **CTeX**；
  - 免安装：**Overleaf** —— 新建项目上传 `main.tex`，在菜单里把编译器设为 XeLaTeX。

## 依赖宏包

`ctex`、`geometry`、`setspace`、`amsmath`、`amssymb`、`bm`、`graphicx`、`booktabs`、`caption`、`algorithm`、`algpseudocode`、`listings`、`xcolor`、`fancyhdr`、`hyperref`。TeX Live 完整安装和 Overleaf 都自带，无需手动装。

## 要填什么

- **标题**：点明研究对象 + 核心方法，别抄赛题原标题。
- **摘要**：每个子问题都要有量化结果（每问必有一数）。
- **各章**：按 `main.tex` 里注释的"红线"提示写。
- **图片**：放进 `figures/` 目录，取消对应 `\includegraphics` 行的注释。
- **参考文献**：≥6 条，GB/T 7714 格式，禁止 CSDN/知乎/百度百科/AI 工具。
- **附录**：放完整可运行代码（2026 规则：缺代码或跑不起来可能取消资格）。

## 匿名（国赛硬要求）

正文里不能出现**学校、姓名、指导教师、学号、联系方式**。模板的 `\author{}` 和页眉已留空；编号页由组委会系统/当年官方模板生成，不在本文件里。交卷前用 kit 的脚本扫一遍：

```bash
bash ../../skills/cumcm-award-gate/scripts/pdf_qa.sh 你的论文.pdf --anonymous
```

## 常见坑

- **中文不显示或报错**：没用 XeLaTeX，或没装 ctex —— 改用 `xelatex` 编译。
- **附录代码里的中文注释变方块**：listings 的等宽字体缺中文字形 —— 代码注释建议用英文。
- **目录/页码/引用显示为问号或不对**：只编译了一次 —— 连编两次即可。
