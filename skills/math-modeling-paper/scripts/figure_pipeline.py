#!/usr/bin/env python3
"""Reproducible CUMCM figure generator driven by a JSON manifest."""
from __future__ import annotations
import argparse, csv, hashlib, json, re
from pathlib import Path
try:
    import matplotlib as mpl
    mpl.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
except ImportError as exc:
    raise SystemExit("Install matplotlib first: pip install matplotlib") from exc

COLORS = ["#4472A8", "#D9822B", "#5A9367", "#9B59B6", "#B44C4C", "#5F6B7A"]
STYLES = ["-", "--", "-.", ":"]
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Microsoft YaHei", "SimHei", "DejaVu Sans"],
    "font.size": 8,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "legend.frameon": False,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})

def numbers(values, label):
    if not isinstance(values, list) or not values:
        raise ValueError(f"{label} must be a non-empty list")
    try:
        return [float(v) for v in values]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc

def source_data(item, base):
    if "data" in item and "source" in item:
        raise ValueError(f"{item['id']}: use data or source, not both")
    if "source" not in item:
        return item.get("data", {})
    path = base / item["source"]
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        return {k: [float(r[k]) if _floatable(r[k]) else r[k] for r in rows] for k in rows[0]}
    raise ValueError("source must be .json or .csv")

def _floatable(value):
    try:
        float(value); return True
    except (TypeError, ValueError):
        return False

def series(item, data):
    value = item.get("series", data.get("series"))
    if value is not None:
        if not isinstance(value, list) or not value: raise ValueError(f"{item['id']}: series is empty")
        return value
    if "x" in item or "x" in data:
        return [{"name": item.get("name", "data"), "x": item.get("x", data["x"]), "y": item.get("y", data.get("y")), "z": item.get("z", data.get("z"))}]
    raise ValueError(f"{item['id']}: x/y data or series is required")

def axes_style(ax, item):
    ax.set_title(item.get("title", ""), pad=8)
    ax.set_xlabel(item.get("xlabel", "")); ax.set_ylabel(item.get("ylabel", ""))
    if item.get("grid", True): ax.grid(True, color="#D9DEE5", linewidth=.55, alpha=.8); ax.set_axisbelow(True)
    if item.get("legend", True) and ax.get_legend_handles_labels()[0]: ax.legend()

def line_plot(item, data):
    fig, ax = plt.subplots(figsize=item.get("figsize", [6.2, 3.8]))
    for i, s in enumerate(series(item, data)):
        x, y = numbers(s.get("x"), f"{item['id']}.x"), numbers(s.get("y"), f"{item['id']}.y")
        if len(x) != len(y): raise ValueError(f"{item['id']}: x/y lengths differ")
        ax.plot(x, y, label=s.get("name", f"series {i+1}"), color=s.get("color", COLORS[i % len(COLORS)]), linestyle=s.get("linestyle", STYLES[i % len(STYLES)]), marker=s.get("marker", ""), linewidth=1.5)
    axes_style(ax, item); return fig

def scatter_plot(item, data):
    fig, ax = plt.subplots(figsize=item.get("figsize", [5.4, 4.0])); xs=[]; ys=[]
    for i, s in enumerate(series(item, data)):
        x, y = numbers(s.get("x"), f"{item['id']}.x"), numbers(s.get("y"), f"{item['id']}.y")
        if len(x) != len(y): raise ValueError(f"{item['id']}: x/y lengths differ")
        xs += x; ys += y; ax.scatter(x, y, label=s.get("name", f"series {i+1}"), color=s.get("color", COLORS[i % len(COLORS)]), s=s.get("size", 24), alpha=.82, edgecolors="white", linewidths=.3)
    if item.get("trendline") and len(xs) > 1:
        xb=sum(xs)/len(xs); yb=sum(ys)/len(ys); den=sum((z-xb)**2 for z in xs); slope=sum((a-xb)*(b-yb) for a,b in zip(xs,ys))/den if den else 0; intercept=yb-slope*xb
        ax.plot([min(xs), max(xs)], [slope*min(xs)+intercept, slope*max(xs)+intercept], "--", color="#333333", label="linear fit")
    axes_style(ax, item); return fig

def bar_plot(item, data):
    labels=item.get("labels", data.get("labels")); values=item.get("values", data.get("values"))
    if not labels or values is None or len(labels) != len(values): raise ValueError(f"{item['id']}: labels/values mismatch")
    values=numbers(values, f"{item['id']}.values"); order=sorted(range(len(values)), key=lambda i: values[i], reverse=item.get("descending", True)); labels=[str(labels[i]) for i in order]; values=[values[i] for i in order]
    fig, ax=plt.subplots(figsize=item.get("figsize", [6.2,3.8])); horizontal=item.get("horizontal", False)
    if horizontal: ax.barh(labels, values, color=item.get("color", COLORS[0]), alpha=.88); ax.set_xlabel(item.get("xlabel", "")); ax.set_ylabel(item.get("ylabel", ""))
    else: ax.bar(labels, values, color=item.get("color", COLORS[0]), alpha=.88); ax.set_xlabel(item.get("xlabel", "")); ax.set_ylabel(item.get("ylabel", "")); ax.tick_params(axis="x", rotation=item.get("xtick_rotation", 0))
    axes_style(ax, item); return fig

def interval_plot(item, data):
    intervals=item.get("intervals", data.get("intervals"))
    if not intervals: raise ValueError(f"{item['id']}: intervals are required")
    fig, ax=plt.subplots(figsize=item.get("figsize", [6.4, max(2.5, .45*len(intervals)+1.5)]))
    for i, entry in enumerate(intervals):
        a,b=float(entry["start"]),float(entry["end"])
        if b<a: raise ValueError(f"{item['id']}: end before start")
        color=entry.get("color", COLORS[i % len(COLORS)]); ax.plot([a,b],[i,i], color=color, linewidth=7, solid_capstyle="round"); ax.scatter([a,b],[i,i], color="white", edgecolors=color, zorder=3, s=24)
    ax.set_yticks(range(len(intervals))); ax.set_yticklabels([str(x.get("name", i+1)) for i,x in enumerate(intervals)]); ax.set_xlabel(item.get("xlabel", "Time")); ax.set_title(item.get("title", ""), pad=8); ax.grid(axis="x", color="#D9DEE5", linewidth=.55); return fig

def sensitivity_plot(item, data):
    fig=line_plot(item, data); baseline=item.get("baseline", data.get("baseline"))
    if baseline is not None:
        ax=fig.axes[0]; ax.axvline(float(baseline), color="#555555", linestyle=":", linewidth=1.0, label="baseline"); ax.legend()
    return fig

def trajectory_plot(item, data):
    fig=plt.figure(figsize=item.get("figsize", [6.3,5.0])); ax=fig.add_subplot(111, projection="3d")
    for i,s in enumerate(series(item,data)):
        x,y,z=numbers(s.get("x"),f"{item['id']}.x"),numbers(s.get("y"),f"{item['id']}.y"),numbers(s.get("z"),f"{item['id']}.z")
        if not len(x)==len(y)==len(z): raise ValueError(f"{item['id']}: x/y/z lengths differ")
        ax.plot(x,y,z,label=s.get("name",f"series {i+1}"),color=s.get("color",COLORS[i%len(COLORS)]),linestyle=s.get("linestyle",STYLES[i%len(STYLES)]),linewidth=1.5)
    ax.set_xlabel(item.get("xlabel","x")); ax.set_ylabel(item.get("ylabel","y")); ax.set_zlabel(item.get("zlabel","z")); ax.set_title(item.get("title",""),pad=10); ax.grid(True,alpha=.35); ax.legend(); return fig

def flowchart_plot(item, data):
    nodes=item.get("nodes",data.get("nodes")); edges=item.get("edges",data.get("edges",[]))
    if not nodes: raise ValueError(f"{item['id']}: nodes are required")
    levels={}
    for n in nodes: levels.setdefault(n.get("level",0),[]).append(n)
    pos={}
    for level, group in levels.items():
        for i,n in enumerate(group): pos[n["id"]]=((i+1)/(len(group)+1),1-.18*float(level))
    fig,ax=plt.subplots(figsize=item.get("figsize",[8,4.8])); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    for edge in edges: ax.add_patch(FancyArrowPatch(pos[edge[0]],pos[edge[1]],arrowstyle="-|>",mutation_scale=12,linewidth=.9,color="#667085"))
    for n in nodes:
        x,y=pos[n["id"]]; w,h=n.get("width",.18),n.get("height",.09); ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle="round,pad=.012,rounding_size=.02",facecolor=n.get("color","#EAF0F6"),edgecolor="#4472A8")); ax.text(x,y,str(n.get("label",n["id"])),ha="center",va="center",fontsize=n.get("fontsize",8),wrap=True)
    if item.get("title"): ax.set_title(item["title"],pad=8)
    return fig

PLOTTERS={"line":line_plot,"scatter":scatter_plot,"bar":bar_plot,"sensitivity":sensitivity_plot,"interval":interval_plot,"trajectory_3d":trajectory_plot,"flowchart":flowchart_plot}

def save_figure(fig, base, formats):
    base.parent.mkdir(parents=True,exist_ok=True); files=[]
    for fmt in formats:
        fmt=fmt.lower().lstrip(".")
        if fmt not in {"svg","pdf","png"}: raise ValueError(f"unsupported format: {fmt}")
        path=base.with_suffix("."+fmt); kwargs={"bbox_inches":"tight"}
        if fmt=="png": kwargs.update(dpi=600,facecolor="white")
        fig.savefig(path,**kwargs); files.append(path)
    plt.close(fig); return files

def safe_name(value): return re.sub(r"[^0-9A-Za-z_.-]+","_",str(value)).strip("._") or "figure"

def generate(manifest_path, out_dir, formats):
    manifest=json.loads(manifest_path.read_text(encoding="utf-8")); entries=manifest.get("figures") if isinstance(manifest,dict) else None
    if not isinstance(entries,list) or not entries: raise ValueError("manifest must contain a non-empty figures list")
    seen=set(); result=[]
    for item in entries:
        fid,typ=item.get("id"),item.get("type")
        if not fid or fid in seen: raise ValueError(f"duplicate or missing figure id: {fid}")
        if typ not in PLOTTERS: raise ValueError(f"{fid}: unsupported type {typ}")
        if not item.get("claim") or not item.get("caption"): raise ValueError(f"{fid}: claim and caption are required")
        seen.add(fid); fig=PLOTTERS[typ](item,source_data(item,manifest_path.parent)); files=save_figure(fig,out_dir/safe_name(fid),formats)
        result.append({"id":fid,"type":typ,"claim":item["claim"],"caption":item["caption"],"files":[str(x) for x in files],"sha256":[hashlib.sha256(x.read_bytes()).hexdigest() for x in files]})
    (out_dir/"figure_manifest.generated.json").write_text(json.dumps({"manifest":str(manifest_path),"figures":result},ensure_ascii=False,indent=2),encoding="utf-8")
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--manifest",required=True,type=Path); p.add_argument("--out-dir",required=True,type=Path); p.add_argument("--formats",default="svg,pdf,png"); a=p.parse_args(); result=generate(a.manifest.resolve(),a.out_dir.resolve(),[x.strip() for x in a.formats.split(",") if x.strip()]); [print(f"{x['id']}: {', '.join(x['files'])}") for x in result]

if __name__=="__main__": main()
