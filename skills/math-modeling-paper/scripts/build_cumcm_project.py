#!/usr/bin/env python3
"""Build a CUMCM paper project from content/figure contracts.

The builder owns assembly and validation, not mathematical authorship.  The
paper body is supplied as LaTeX in ``paper_content.json``; figures are made
from real data by ``figure_pipeline.py`` when a manifest is present.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List


PLACEHOLDERS = ["XXX", "……", "此处插图", "待补", "TODO", "PLACEHOLDER"]
GRAPHICS_RE = re.compile(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}")


def read_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def required_text(content: Dict[str, Any], key: str) -> str:
    value = content.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"paper_content.json requires non-empty string: {key}")
    return value


def optional_text(content: Dict[str, Any], key: str, default: str = "") -> str:
    value = content.get(key, default)
    if not isinstance(value, str):
        raise ValueError(f"paper_content.json field {key!r} must be a string")
    return value


def template_preamble(template: Path) -> str:
    text = template.read_text(encoding="utf-8")
    marker = "\\begin{document}"
    if marker not in text:
        raise ValueError(f"template has no {marker}: {template}")
    return text.split(marker, 1)[0].rstrip() + "\n"


def make_tex(content: Dict[str, Any], template: Path) -> str:
    title = required_text(content, "title")
    abstract = required_text(content, "abstract_tex")
    body = required_text(content, "body_tex")
    keywords = required_text(content, "keywords")
    ai = optional_text(content, "ai_statement", "本参赛队在竞赛过程中使用了可复现的程序工具，所有模型假设、数据处理和结论均由参赛队独立核验。")
    bibliography = optional_text(content, "bibliography_tex", "% 未提供参考文献。提交前请补充正文实际引用的文献。")
    appendix = optional_text(content, "appendix_tex", "% 未提供附录。提交前请补充支撑材料与完整代码。")
    preamble = template_preamble(template)
    return """{preamble}
\\begin{{document}}
\\pagenumbering{{arabic}}

\\begin{{center}}
  {{\\heiti\\xiaoer {title}}}
\\end{{center}}
\\vspace{{18pt}}

\\begin{{center}}
  {{\\heiti\\sanhao 摘要}}
\\end{{center}}
\\vspace{{6pt}}

{abstract}

\\vspace{{6pt}}
\\noindent{{\\heiti 关键词：}}\\quad {keywords}
\\newpage

{body}

% ==================== AI 工具使用声明 ====================
\\section*{{AI 工具使用声明}}
\\addcontentsline{{toc}}{{section}}{{AI 工具使用声明}}
{ai}

% ==================== 参考文献 ====================
\\section*{{参考文献}}
\\addcontentsline{{toc}}{{section}}{{参考文献}}
{bibliography}

% ==================== 附录 ====================
\\newpage
\\section*{{附录}}
\\addcontentsline{{toc}}{{section}}{{附录}}
{appendix}

\\end{{document}}
""".format(preamble=preamble, title=title, abstract=abstract, keywords=keywords, body=body, ai=ai, bibliography=bibliography, appendix=appendix)


def graphic_candidates(project: Path, ref: str) -> Iterable[Path]:
    path = Path(ref)
    if path.suffix:
        yield project / path
    else:
        for ext in (".pdf", ".png", ".svg", ".jpg", ".jpeg"):
            yield project / path.with_suffix(ext)


def validate_tex(tex: str, project: Path) -> List[str]:
    errors: List[str] = []
    for marker in PLACEHOLDERS:
        if marker in tex:
            errors.append(f"placeholder remains in main.tex: {marker}")
    if tex.count("\\begin{document}") != 1 or tex.count("\\end{document}") != 1:
        errors.append("main.tex must contain exactly one document begin/end")
    for ref in GRAPHICS_RE.findall(tex):
        if not any(candidate.exists() for candidate in graphic_candidates(project, ref)):
            errors.append(f"missing graphics file: {ref}")
    return errors


def run_figures(script: Path, manifest: Path, out_dir: Path, formats: str) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, str(script), "--manifest", str(manifest), "--out-dir", str(out_dir), "--formats", formats]
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if completed.returncode:
        raise RuntimeError(f"figure generation failed:\n{completed.stdout}\n{completed.stderr}")
    generated_manifest = out_dir / "figure_manifest.generated.json"
    return read_json(generated_manifest) if generated_manifest.exists() else {"stdout": completed.stdout}


def find_xelatex() -> str | None:
    command = shutil.which("xelatex")
    return command


def compile_tex(project: Path, passes: int = 2) -> Dict[str, Any]:
    xelatex = find_xelatex()
    if not xelatex:
        return {"status": "skipped", "reason": "xelatex not found; use Overleaf XeLaTeX"}
    logs = []
    for index in range(passes):
        completed = subprocess.run([xelatex, "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=project, capture_output=True, text=True, encoding="utf-8", errors="replace")
        log = project / f"xelatex-pass-{index + 1}.log"
        log.write_text((completed.stdout or "") + "\n" + (completed.stderr or ""), encoding="utf-8")
        logs.append(str(log))
        if completed.returncode:
            raise RuntimeError(f"XeLaTeX failed on pass {index + 1}; see {log}")
    return {"status": "compiled", "passes": passes, "logs": logs, "pdf": str(project / "main.pdf")}


def build(project: Path, content_path: Path, template: Path, manifest: Path | None, formats: str, compile_pdf: bool) -> Dict[str, Any]:
    project.mkdir(parents=True, exist_ok=True)
    (project / "figures").mkdir(exist_ok=True)
    (project / "figure_data").mkdir(exist_ok=True)
    (project / "scripts").mkdir(exist_ok=True)
    content = read_json(content_path)
    tex = make_tex(content, template)
    (project / "main.tex").write_text(tex, encoding="utf-8")
    figure_result = None
    if manifest is None:
        candidate = project / "figure_manifest.json"
        manifest = candidate if candidate.exists() else None
    if manifest is not None:
        figure_script = Path(__file__).with_name("figure_pipeline.py")
        figure_result = run_figures(figure_script, manifest.resolve(), (project / "figures").resolve(), formats)
    errors = validate_tex(tex, project)
    report: Dict[str, Any] = {"project": str(project.resolve()), "main_tex": str((project / "main.tex").resolve()), "figures": figure_result, "validation": {"status": "passed" if not errors else "failed", "errors": errors}}
    if errors:
        (project / "build_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        raise RuntimeError("; ".join(errors))
    if compile_pdf:
        report["latex"] = compile_tex(project)
    else:
        report["latex"] = {"status": "not requested"}
    (project / "build_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path, help="final paper project directory")
    parser.add_argument("--content", required=True, type=Path, help="paper_content.json")
    parser.add_argument("--template", required=True, type=Path, help="templates/cumcm-latex/main.tex")
    parser.add_argument("--manifest", type=Path, help="figure_manifest.json; defaults to project/figure_manifest.json")
    parser.add_argument("--formats", default="svg,pdf,png")
    parser.add_argument("--compile", action="store_true", help="compile main.tex twice when XeLaTeX is available")
    args = parser.parse_args()
    report = build(args.project.resolve(), args.content.resolve(), args.template.resolve(), args.manifest.resolve() if args.manifest else None, args.formats, args.compile)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
