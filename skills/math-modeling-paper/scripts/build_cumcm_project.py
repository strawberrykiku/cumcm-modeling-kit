#!/usr/bin/env python3
"""Build an editable CUMCM paper project from content/figure contracts.

The builder owns deterministic file assembly and validation, not mathematical
authorship.  New projects are split into editable LaTeX section files,
question-level code files, figure scripts, and figure data.  The legacy
``body_tex`` field remains supported and is written as one legacy body file.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


PLACEHOLDERS = ["XXX", "……", "此处插图", "待补", "TODO", "PLACEHOLDER"]
GRAPHICS_RE = re.compile(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}")
INPUT_RE = re.compile(r"\\input\{([^}]+)\}")

# The order is the standard CUMCM paper order.  Optional sections are only
# written/included when the corresponding content is supplied.
SECTION_SPECS: List[Tuple[str, str]] = [
    ("problem_restatement", "02_problem_restatement.tex"),
    ("problem_analysis", "03_problem_analysis.tex"),
    ("model_assumptions", "04_model_assumptions.tex"),
    ("notation", "05_notation.tex"),
    ("data_processing", "06_data_processing.tex"),
    ("modeling_solution", "07_modeling_solution.tex"),
    ("model_validation", "08_model_validation.tex"),
    ("model_evaluation", "09_model_evaluation.tex"),
    ("model_extension", "10_model_extension.tex"),
]


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


def section_map(content: Dict[str, Any]) -> Dict[str, str]:
    """Read the new semantic section map, validating every value."""
    value = content.get("sections")
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("paper_content.json field 'sections' must be an object")
    result: Dict[str, str] = {}
    for key, text in value.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("paper_content.json section keys must be non-empty strings")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"paper_content.json section must be non-empty string: {key}")
        result[key] = text
    return result


def file_entries(content: Dict[str, Any], key: str) -> List[Dict[str, str]]:
    """Validate a list of editable text-file entries."""
    value = content.get(key, [])
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"paper_content.json field {key!r} must be a list")
    entries: List[Dict[str, str]] = []
    seen_paths = set()
    for index, entry in enumerate(value):
        if not isinstance(entry, dict):
            raise ValueError(f"{key}[{index}] must be an object")
        path = entry.get("path")
        text = entry.get("content")
        if not isinstance(path, str) or not path.strip():
            raise ValueError(f"{key}[{index}].path must be a non-empty string")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"{key}[{index}].content must be a non-empty string")
        normalized = path.replace("\\", "/")
        if normalized in seen_paths:
            raise ValueError(f"{key} contains duplicate path: {path}")
        seen_paths.add(normalized)
        entries.append({"path": path, "content": text})
    return entries


def safe_relative_path(value: str, field: str) -> Path:
    """Return a safe project-relative path and reject traversal/absolute paths."""
    raw = value.replace("\\", "/").strip()
    if not raw or raw.startswith("/") or re.match(r"^[A-Za-z]:", raw):
        raise ValueError(f"{field} path must be relative to the project: {value!r}")
    parts = raw.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"{field} path contains an invalid component: {value!r}")
    return Path(*parts)


def write_preserving(path: Path, text: str, overwrite: bool, state: Dict[str, List[str]]) -> None:
    """Write a generated artifact unless an existing user file is protected."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        state["preserved"].append(str(path))
        return
    path.write_text(text, encoding="utf-8")
    state["written"].append(str(path))


def template_preamble(template: Path) -> str:
    text = template.read_text(encoding="utf-8")
    marker = "\\begin{document}"
    if marker not in text:
        raise ValueError(f"template has no {marker}: {template}")
    return text.split(marker, 1)[0].rstrip() + "\n"


def abstract_section(content: Dict[str, Any]) -> str:
    title = required_text(content, "title")
    abstract = required_text(content, "abstract_tex")
    keywords = required_text(content, "keywords")
    return """\\pagenumbering{{arabic}}
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
""".format(title=title, abstract=abstract, keywords=keywords)


def wrapped_tail_sections(content: Dict[str, Any]) -> Dict[str, str]:
    """Return generated AI statement, references, and appendix section files."""
    ai = optional_text(
        content,
        "ai_statement",
        "本参赛队在竞赛过程中使用了可复现的程序工具，所有模型假设、数据处理和结论均由参赛队独立核验。",
    )
    bibliography = optional_text(
        content,
        "bibliography_tex",
        "% 未提供参考文献。提交前请补充正文实际引用的文献。",
    )
    appendix = optional_text(
        content,
        "appendix_tex",
        "% 未提供附录。提交前请补充支撑材料与完整代码。",
    )
    return {
        "11_ai_statement.tex": "\\section*{AI 工具使用声明}\n\\addcontentsline{toc}{section}{AI 工具使用声明}\n" + ai + "\n",
        "12_references.tex": "\\section*{参考文献}\n\\addcontentsline{toc}{section}{参考文献}\n" + bibliography + "\n",
        "13_appendix.tex": "\\newpage\n\\section*{附录}\n\\addcontentsline{toc}{section}{附录}\n" + appendix + "\n",
    }


def legacy_body_section(content: Dict[str, Any]) -> str:
    """Support the old monolithic body contract without losing editability."""
    body = content.get("body_tex")
    if not isinstance(body, str) or not body.strip():
        raise ValueError("paper_content.json requires 'sections' or non-empty 'body_tex'")
    return body


def section_payloads(content: Dict[str, Any]) -> Tuple[Dict[str, str], bool]:
    """Build ``relative .tex path -> content`` and flag legacy body fallback."""
    sections = section_map(content)
    payloads: Dict[str, str] = {"01_abstract.tex": abstract_section(content)}
    legacy = not bool(sections)
    if sections:
        known = {key for key, _ in SECTION_SPECS}
        for key, filename in SECTION_SPECS:
            if key in sections:
                payloads[filename] = sections[key]
        # Preserve custom sections after the standard order.  The key is made
        # into a deterministic, user-visible filename without allowing paths.
        extras = [(key, value) for key, value in sections.items() if key not in known]
        for index, (key, value) in enumerate(extras, start=1):
            stem = re.sub(r"[^0-9A-Za-z_-]+", "_", key).strip("_") or f"custom_{index}"
            filename = f"20_{stem}.tex"
            while filename in payloads:
                index += 1
                filename = f"20_{stem}_{index}.tex"
            payloads[filename] = value
    else:
        payloads["02_body_legacy.tex"] = legacy_body_section(content)
    payloads.update(wrapped_tail_sections(content))
    return payloads, legacy


def make_main_tex(included_sections: Iterable[str]) -> str:
    """Create a thin editable main.tex that inputs each section file."""
    # Keep the preamble editable as its own file too.  It contains the
    # ``\\documentclass`` declaration and must therefore be the first input.
    lines = ["% Generated entry point; edit tex/sections/*.tex for content.", "\\input{tex/preamble.tex}", "\\begin{document}"]
    for relative in included_sections:
        normalized = relative.replace("\\", "/")
        lines.append(f"\\input{{{normalized}}}")
    lines.extend(["", "\\end{document}", ""])
    return "\n".join(lines)


def graphic_candidates(project: Path, ref: str) -> Iterable[Path]:
    path = Path(ref)
    if path.suffix:
        yield project / path
    else:
        for ext in (".pdf", ".png", ".svg", ".jpg", ".jpeg"):
            yield project / path.with_suffix(ext)


def validate_tex(tex: str, project: Path, section_text: str = "") -> List[str]:
    errors: List[str] = []
    source = tex + "\n" + section_text
    for marker in PLACEHOLDERS:
        if marker in source:
            errors.append(f"placeholder remains in project LaTeX: {marker}")
    if tex.count("\\begin{document}") != 1 or tex.count("\\end{document}") != 1:
        errors.append("main.tex must contain exactly one document begin/end")
    if section_text.count("\\begin{document}") or section_text.count("\\end{document}"):
        errors.append("section files must not contain document begin/end markers")
    for ref in GRAPHICS_RE.findall(source):
        if not any(candidate.exists() for candidate in graphic_candidates(project, ref)):
            errors.append(f"missing graphics file: {ref}")
    for ref in INPUT_RE.findall(tex):
        path = project / ref
        candidates = [path] if path.suffix else [path.with_suffix(".tex"), path]
        if not any(candidate.exists() for candidate in candidates):
            errors.append(f"missing input section file: {ref}")
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


def build(
    project: Path,
    content_path: Path,
    template: Path,
    manifest: Path | None,
    formats: str,
    compile_pdf: bool,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Write an editable project and assemble its generated ``main.tex``.

    ``overwrite=False`` protects section/code/figure-source files that the
    user may have edited after a previous build.  ``main.tex`` and the report
    are always regenerated because they are derived files.
    """
    project.mkdir(parents=True, exist_ok=True)
    (project / "figures").mkdir(exist_ok=True)
    (project / "figure_data").mkdir(exist_ok=True)
    (project / "scripts" / "figures").mkdir(parents=True, exist_ok=True)
    (project / "tex" / "sections").mkdir(parents=True, exist_ok=True)
    (project / "code").mkdir(exist_ok=True)
    (project / "notes").mkdir(exist_ok=True)
    content = read_json(content_path)
    payloads, legacy_body = section_payloads(content)
    state: Dict[str, List[str]] = {"written": [], "preserved": []}

    preamble_path = project / "tex" / "preamble.tex"
    write_preserving(preamble_path, template_preamble(template), overwrite, state)
    section_paths: List[str] = []
    section_text = []
    for filename, text in payloads.items():
        path = project / "tex" / "sections" / filename
        write_preserving(path, text, overwrite, state)
        section_paths.append(f"tex/sections/{filename}")
        # Validate the newly generated content even when an existing file was
        # preserved; reading the file makes validation reflect user edits.
        section_text.append(path.read_text(encoding="utf-8"))

    code_paths: List[str] = []
    for entry in file_entries(content, "code_files"):
        relative = safe_relative_path(entry["path"], "code_files")
        path = project / "code" / relative
        write_preserving(path, entry["content"], overwrite, state)
        code_paths.append(str(Path("code") / relative).replace("\\", "/"))

    figure_script_paths: List[str] = []
    for entry in file_entries(content, "figure_scripts"):
        relative = safe_relative_path(entry["path"], "figure_scripts")
        path = project / "scripts" / "figures" / relative
        write_preserving(path, entry["content"], overwrite, state)
        figure_script_paths.append(str(Path("scripts") / "figures" / relative).replace("\\", "/"))

    figure_data_paths: List[str] = []
    for entry in file_entries(content, "figure_data_files"):
        relative = safe_relative_path(entry["path"], "figure_data_files")
        path = project / "figure_data" / relative
        write_preserving(path, entry["content"], overwrite, state)
        figure_data_paths.append(str(Path("figure_data") / relative).replace("\\", "/"))

    notes_paths: List[str] = []
    for entry in file_entries(content, "notes_files"):
        relative = safe_relative_path(entry["path"], "notes_files")
        path = project / "notes" / relative
        write_preserving(path, entry["content"], overwrite, state)
        notes_paths.append(str(Path("notes") / relative).replace("\\", "/"))

    main_tex = make_main_tex(section_paths)
    main_path = project / "main.tex"
    main_path.write_text(main_tex, encoding="utf-8")

    # Keep a local copy of the content contract when the source lives outside
    # the project.  It is a convenient audit trail, but user-edited split files
    # remain the source of truth unless --overwrite is requested.
    local_content = project / "paper_content.json"
    if content_path.resolve() != local_content.resolve() and (overwrite or not local_content.exists()):
        local_content.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    figure_result = None
    if manifest is None:
        candidate = project / "figure_manifest.json"
        manifest = candidate if candidate.exists() else None
    local_manifest: Path | None = None
    if manifest is not None:
        local_manifest = project / "figure_manifest.json"
        if manifest.resolve() != local_manifest.resolve():
            write_preserving(local_manifest, manifest.read_text(encoding="utf-8"), overwrite, state)
        figure_script = Path(__file__).with_name("figure_pipeline.py")
        # Run against the project-local copy so ``source`` paths such as
        # ``figure_data/results.json`` remain reproducible after the project
        # directory is moved or uploaded to Overleaf.
        figure_result = run_figures(figure_script, local_manifest.resolve(), (project / "figures").resolve(), formats)
    errors = validate_tex(main_tex, project, "\n".join(section_text))
    report: Dict[str, Any] = {
        "project": str(project.resolve()),
        "main_tex": str(main_path.resolve()),
        "paper_content": str(local_content.resolve()),
        "figure_manifest": str(local_manifest.resolve()) if local_manifest is not None else None,
        "layout": {
            "mode": "split",
            "legacy_body_fallback": legacy_body,
            "section_files": section_paths,
            "code_files": code_paths,
            "figure_script_files": figure_script_paths,
            "figure_data_files": figure_data_paths,
            "notes_files": notes_paths,
            "written_files": state["written"],
            "preserved_files": state["preserved"],
        },
        "figures": figure_result,
        "validation": {"status": "passed" if not errors else "failed", "errors": errors},
    }
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
    parser.add_argument("--overwrite", action="store_true", help="overwrite editable split files from paper_content.json")
    args = parser.parse_args()
    report = build(
        args.project.resolve(),
        args.content.resolve(),
        args.template.resolve(),
        args.manifest.resolve() if args.manifest else None,
        args.formats,
        args.compile,
        args.overwrite,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
