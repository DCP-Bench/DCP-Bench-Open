#!/usr/bin/env python3
"""Generate the static DCP-Bench Open website from dcp-bench-open.jsonl.

Usage:
    python jsonl_convert.py   # optional, to refresh the jsonl from dataset/
    python generate_site.py

Output: site/ (committed to the repo, deployed to GitHub Pages via Actions).
Requires only the Python standard library.
"""

import html
import json
import re
import shutil
import subprocess
from pathlib import Path

DATASET_JSONL = Path("dcp-bench-open.jsonl")
WEB_SRC = Path("web")
OUTPUT_DIR = Path("site")
GENERATED_DIR = Path("generated_models")

REPO_URL = "https://github.com/DCP-Bench/DCP-Bench-Open"
RAW_URL = "https://raw.githubusercontent.com/DCP-Bench/DCP-Bench-Open/main"

TITLE = "DCP-Bench Open"
SUBTITLE = (
    "A growing collection of discrete combinatorial problems, with hand-written and "
    "agent-generated models in many frameworks — instances, solutions, and evaluation "
    "results for every model."
)

FRAMEWORK_ORDER = ["CPMpy", "MiniZinc", "OR-Tools"]

VERDICT_STYLES = {
    "solution_valid_and_optimal": ("#16a34a", "solution valid · optimal",
                                   "Model produces a valid solution with the optimal objective value"),
    "solution_valid": ("#2563eb", "solution valid",
                       "Model produces a valid solution (satisfaction problem, or optimality not applicable)"),
    "solution_valid_not_optimal": ("#d97706", "solution valid · not optimal",
                                   "Model produces a valid solution, but the objective value is not optimal"),
    "solution_valid_objective_unknown": ("#0891b2", "solution valid · optimality unknown",
                                         "Model produces a valid solution; optimality was not checked by the evaluation"),
    "solution_not_valid": ("#dc2626", "solution not valid",
                           "The produced solution does not satisfy the ground-truth constraints"),
    "unknown": ("#6b7280", "status unknown",
                "No verdict available (execution failed, model skipped, or evaluation incomplete)"),
}

LEGACY_BADGE = ('<span class="badge outline" title="Imported from the CP-Bench leaderboard '
                '(kostis-init/CP-Bench-Leaderboard-Live) submissions — evaluation performed there, '
                'not re-verified in this repository">legacy · CP-Bench leaderboard</span>')

BADGE_COLORS = {
    "CPMpy": "#0d9488",
    "OR-Tools": "#ea580c",
    "MiniZinc": "#2563eb",
    "hand": "#64748b",
}

ORIGIN_LABELS = {"hand": "hand-written"}


def origin_label(origin: str) -> str:
    return ORIGIN_LABELS.get(origin, origin)

FRAMEWORK_KEYWORDS = {
    "CPMpy": ["from cpmpy import", "import cpmpy"],
    "OR-Tools": ["from ortools import", "import ortools"],
    "MiniZinc": ["import minizinc", "from minizinc", ".mzn"],
}


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


REPO_HEAD = ""


def repo_head_short() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5, check=True,
        ).stdout.strip()
        return out or ""
    except Exception:
        return ""


URL_RE = re.compile(r"https?://[^\s]+")


def linkify(text: str) -> str:
    """Escape text and wrap URLs in anchors."""
    parts = URL_RE.split(esc(text))
    urls = URL_RE.findall(esc(text))
    out = [parts[0]]
    for url in urls:
        out.append(f'<a href="{url}" target="_blank" rel="noopener">{url}</a>')
        out.append(parts[urls.index(url) + 1])
    return "".join(out)


def parse_metadata(metadata: list) -> dict:
    fields = {}
    for line in metadata:
        m = re.match(r"#\s*([A-Za-z][A-Za-z ]*?)\s*:\s*(.*)$", line.strip())
        if m:
            key = m.group(1).strip().lower().replace(" ", "_")
            fields[key] = m.group(2).strip()
    return fields


def detect_frameworks(model_code: str) -> list:
    """Fallback detection used only for jsonl files lacking a `framework` field."""
    found = []
    for fw, keywords in FRAMEWORK_KEYWORDS.items():
        if any(k in model_code for k in keywords):
            found.append(fw)
    return found or ["CPMpy"]


def snippet(text: str, limit: int = 180) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def badge(label: str, key: str = None) -> str:
    color = BADGE_COLORS.get(key or label)
    cls = "" if color else " plain"
    style = f' style="background:{color}"' if color else ""
    return f'<span class="badge{cls}"{style}>{esc(label)}</span>'


def page(title: str, prefix: str, active: str, body: str, description: str = "") -> str:
    nav_items = [
        ("index.html", "Problems", "problems"),
        ("framework.html", "Frameworks", "frameworks"),
        ("stats.html", "Stats", "stats"),
    ]
    nav = [f'<a class="brand" href="{prefix}index.html">{TITLE}</a>']
    for href, label, key in nav_items:
        cls = " active" if key == active else ""
        nav.append(f'<a class="{cls.strip()}" href="{prefix}{href}">{label}</a>')
    nav.append(f'<span class="spacer"></span>')
    nav.append(f'<a class="gh" href="{REPO_URL}" target="_blank" rel="noopener">GitHub</a>')

    if active == "index":
        hero = (
            f'<div class="hero">'
            f'<h1>{TITLE}</h1><p>{SUBTITLE}</p></div>'
        )
    else:
        hero = f'<div class="hero" style="padding-bottom:16px"><h1 style="font-size:1.4rem;margin:0">{esc(title)}</h1></div>'

    footer_head = f" · commit <code>{esc(REPO_HEAD)}</code>" if REPO_HEAD else ""
    head_desc = f'<meta name="description" content="{esc(description)}">' if description else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · {TITLE}</title>
{head_desc}
<link rel="stylesheet" href="{prefix}style.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
</head>
<body>
<header><nav>{"".join(nav)}</nav>{hero}</header>
<main>{body}</main>
<footer>Generated by <code>generate_site.py</code> from <code>dcp-bench-open.jsonl</code>{footer_head} · <a href="{REPO_URL}" target="_blank" rel="noopener">DCP-Bench Open</a></footer>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<script src="{prefix}data.js"></script>
<script src="{prefix}app.js"></script>
</body>
</html>
"""


def code_block(code: str, lang: str, copy_id: str = None, head_label: str = None) -> str:
    head = ""
    if copy_id:
        head = (
            f'<div class="code-head"><span>{esc(head_label or lang)}</span>'
            f'<button type="button" data-copy="{copy_id}">Copy</button></div>'
        )
    return (
        f"{head}<pre class=\"code-block\"><code id=\"{copy_id}\" "
        f'class="language-{lang}">{esc(code)}</code></pre>'
    )


# --------------------------------------------------------------------------
# Generated models (from generated_models/)
# --------------------------------------------------------------------------

def load_generated_models() -> dict:
    """Scan generated_models/<problem>/<framework>/<submission>/ -> {problem: {framework: [entries]}}."""
    out = {}
    if not GENERATED_DIR.is_dir():
        return out
    for problem_dir in GENERATED_DIR.iterdir():
        if not problem_dir.is_dir():
            continue
        by_fw = {}
        for fw_dir in problem_dir.iterdir():
            if not fw_dir.is_dir():
                continue
            entries = []
            for sub_dir in sorted(fw_dir.iterdir()):
                if not sub_dir.is_dir():
                    continue
                metrics_path = sub_dir / "metrics_passed.json"
                if not metrics_path.is_file():
                    continue
                try:
                    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
                except Exception:
                    continue
                model_file = next(
                    (f.name for f in sorted(sub_dir.iterdir())
                     if f.is_file() and f.name.startswith("model.")),
                    None,
                )
                code = ""
                if model_file:
                    try:
                        code = (sub_dir / model_file).read_text(encoding="utf-8")
                    except Exception:
                        code = ""
                entries.append({
                    "submission": sub_dir.name,
                    "metrics": metrics,
                    "model_file": model_file,
                    "code": code,
                })
            if entries:
                fw = entries[0]["metrics"].get("framework", "Unknown")
                by_fw[fw] = entries
        if by_fw:
            out[problem_dir.name] = by_fw
    return out


def verdict_badge(metrics: dict) -> str:
    key = metrics.get("verdict", {}).get("badge", "unknown")
    color, label, tooltip = VERDICT_STYLES.get(key, VERDICT_STYLES["unknown"])
    return (
        f'<span class="badge" style="background:{color}" title="{esc(tooltip)}">'
        f"{esc(label)}</span>"
    )


def framework_dir(fw: str) -> str:
    return {"CPMpy": "cpmpy", "MiniZinc": "minizinc", "OR-Tools": "ortools"}.get(fw, fw.lower())


def generated_model_card(entry: dict) -> str:
    m = entry["metrics"]
    v = m.get("verdict", {})
    gen = m.get("generated_by", {})
    src = m.get("source", {})
    llm = gen.get("base_llm") or "unknown"
    dataset_version = gen.get("dataset_version") or ""

    lines = entry["code"].count("\n") if entry["code"] else 0
    uid = f"{m.get('problem', '')}-{entry['submission']}"
    if entry["model_file"]:
        lang = "minizinc" if entry["model_file"].endswith(".mzn") else "python"
        code = (
            f'<details class="gmodel"><summary>{esc(entry["model_file"])}'
            f" ({lines} lines)</summary>{code_block(entry['code'], lang, copy_id=f'gmod-{uid}')}</details>"
        )
    else:
        code = '<p class="desc">Code file not found.</p>'

    solution = ""
    if v.get("solution"):
        pretty = json.dumps(v["solution"], indent=2, ensure_ascii=False)
        solution = (
            f'<details class="gmodel"><summary>solution</summary>'
            f'{code_block(pretty, "json", copy_id=f"gsol-{uid}")}</details>'
        )

    error = ""
    if v.get("error"):
        error = f'<p class="desc" style="color:#b91c1c;margin:6px 0">{esc(v["error"])}</p>'

    links = []
    if src.get("leaderboard"):
        links.append(f'<a href="{esc(src["leaderboard"])}" target="_blank" rel="noopener">Leaderboard</a>')
    if entry["model_file"]:
        links.append(
            f'<a href="{REPO_URL}/blob/main/generated_models/{esc(m.get("problem", ""))}/{esc(framework_dir(m.get("framework", "")))}/{esc(entry["submission"])}/{esc(entry["model_file"])}" target="_blank" rel="noopener">Model file (GitHub)</a>'
        )
    if src.get("submission_file"):
        links.append(f'<a href="{esc(src["submission_file"])}" target="_blank" rel="noopener">Submission file</a>')
    if src.get("report_file"):
        links.append(f'<a href="{esc(src["report_file"])}" target="_blank" rel="noopener">Report (PDF)</a>')
    if src.get("result_file"):
        links.append(f'<a href="{esc(src["result_file"])}" target="_blank" rel="noopener">Result summary</a>')

    meta_bits = [f"base LLM: {esc(llm)}"]
    if dataset_version:
        meta_bits.append(esc(dataset_version))
    return f"""
    <div class="model-card">
      <div class="model-card-head">
        <div>
          <div class="model-card-title">{esc(entry["submission"])} {LEGACY_BADGE}</div>
          <div class="muted">{" · ".join(meta_bits)}</div>
        </div>
        <div>{verdict_badge(m)}</div>
      </div>
      {error}
      {code}
      {solution}
      <div class="model-card-links">{" · ".join(links)}</div>
    </div>
    """


VALID_BADGE_ORDER = [
    "solution_valid_and_optimal",
    "solution_valid_objective_unknown",
    "solution_valid",
    "solution_valid_not_optimal",
]


def select_best_generated(gen_by_fw: dict) -> dict:
    """Keep at most one generated model per framework: the best valid one
    (valid + optimal preferred for optimisation problems). Frameworks without
    a valid model are dropped."""
    out = {}
    for fw, entries in gen_by_fw.items():
        best, best_rank = None, None
        for entry in entries:
            badge = entry["metrics"].get("verdict", {}).get("badge", "unknown")
            if badge in VALID_BADGE_ORDER:
                rank = VALID_BADGE_ORDER.index(badge)
                if best is None or rank < best_rank:
                    best, best_rank = entry, rank
        if best is not None:
            out[fw] = best
    return out


# --------------------------------------------------------------------------
# Index page (Problem view)
# --------------------------------------------------------------------------

def build_index(problems: list, stats: dict) -> None:
    frameworks = sorted({fw for p in problems for fw in p["frameworks"]})
    origins = sorted({p["origin"] for p in problems})

    fw_opts = "".join(f'<option value="{f}">{f} ({stats["frameworks"][f]})</option>' for f in frameworks)
    origin_opts = "".join(f'<option value="{o}">{origin_label(o)} ({stats["origins"][o]})</option>' for o in origins)

    stats_bar = f"""
    <div class="stat-row">
      <div class="stat"><div class="num">{stats["problems"]}</div><div class="lbl">problems</div></div>
      <div class="stat"><div class="num">{stats["instances"]}</div><div class="lbl">instances</div></div>
      <div class="stat"><div class="num">{stats["models"]}</div><div class="lbl">models</div></div>
      <div class="stat"><div class="num">{stats["generated_models"]}</div><div class="lbl">generated models</div></div>
      <div class="stat"><div class="num">{len(frameworks)}</div><div class="lbl">frameworks</div></div>
    </div>"""

    body = f"""
    {stats_bar}
    <div class="controls">
      <input type="search" id="filter-q" placeholder="Search problems…" autocomplete="off">
      <select id="filter-fw"><option value="">All frameworks</option>{fw_opts}</select>
      <select id="filter-origin"><option value="">All origins</option>{origin_opts}</select>
    </div>
    <p class="result-count" id="result-count"></p>
    <div class="cards" id="cards"></div>
    """

    (OUTPUT_DIR / "index.html").write_text(
        page("Problems", "", "index", body, SUBTITLE), encoding="utf-8"
    )


def coverage_matrix(problems: list, frameworks: list) -> str:
    rows = []
    for p in problems:
        cells = []
        for fw in frameworks:
            ok = fw in p["frameworks"]
            cells.append(
                f'<td class="{"yes" if ok else "no"}">{"✓" if ok else "·"}</td>'
            )
        rows.append(
            f'<tr><td class="cell-id"><a href="problems/{p["id"]}.html">{esc(p["id"])}</a></td>'
            f'{"".join(cells)}</tr>'
        )
    header = "".join(f"<th>{esc(f)}</th>" for f in frameworks)
    return (
        '<table class="matrix"><thead><tr><th>problem</th>'
        f"{header}</tr></thead><tbody>{''.join(rows)}</tbody></table>"
    )


# --------------------------------------------------------------------------
# Problem pages
# --------------------------------------------------------------------------

def var_chips_short(vars_list: list) -> str:
    return "".join(f'<span class="chip">{esc(v)}</span>' for v in vars_list) or ""


def instance_card_html(inst, i: int, idx: int, is_example: bool, example_solution, decision_vars: list) -> str:
    label = "Example instance" if is_example else f"Instance {i}"
    pretty = json.dumps(inst, indent=2, ensure_ascii=False)
    data_pane = code_block(pretty, "json", copy_id=f"inst-{idx}-{i}")
    if is_example and example_solution:
        sol_code = json.dumps(example_solution, indent=2, ensure_ascii=False)
        solution_pane = (
            f'<div class="chip-row">{var_chips_short(decision_vars)}</div>'
            f'{code_block(sol_code, "json", copy_id=f"sol-{idx}-{i}")}'
        )
    else:
        solution_pane = '<p class="desc">No solution yet, will be added shortly.</p>'
    return (
        f'<details class="instance"><summary>{label}</summary>'
        f'<div class="tab-group">'
        f'<div class="tab-bar">'
        f'<button class="tab-btn active" type="button" data-tab="data">Data</button>'
        f'<button class="tab-btn" type="button" data-tab="solution">Solution</button>'
        f'</div>'
        f'<div class="tab-pane active" data-pane="data">{data_pane}</div>'
        f'<div class="tab-pane" data-pane="solution">{solution_pane}</div>'
        f'</div></details>'
    )


def instances_section_html(p: dict, idx: int) -> str:
    insts = p["instances"] or ([p["example_instance"]] if p["example_instance"] else [])
    if not insts:
        if p["example_solution"]:
            sol_code = json.dumps(p["example_solution"], indent=2, ensure_ascii=False)
            return (
                '<details class="card-box instances-box">'
                '<summary><h3>Instances</h3></summary>'
                '<details class="instance"><summary>Example instance</summary>'
                '<div class="tab-group"><div class="tab-bar">'
                '<button class="tab-btn active" type="button" data-tab="data">Data</button>'
                '<button class="tab-btn" type="button" data-tab="solution">Solution</button>'
                '</div>'
                f'<div class="tab-pane active" data-pane="data"><p class="desc">No instance data available.</p></div>'
                f'<div class="tab-pane" data-pane="solution">{code_block(sol_code, "json", copy_id=f"sol-{idx}-0")}</div>'
                '</div></details></details>'
            )
        return (
            '<details class="card-box instances-box">'
            '<summary><h3>Instances</h3></summary>'
            '<p class="desc">No instances available.</p></details>'
        )
    cards = "".join(
        instance_card_html(
            inst, i, idx,
            is_example=(i == 1),
            example_solution=p["example_solution"],
            decision_vars=p["decision_variables"],
        )
        for i, inst in enumerate(insts, 1)
    )
    return (
        f'<details class="card-box instances-box">'
        f'<summary><h3>Instances</h3></summary>{cards}</details>'
    )


def models_section_html(p: dict, meta: dict, idx: int, generated: dict) -> str:
    best = select_best_generated(generated)
    buttons = [
        f'<button class="tab-btn active" type="button" data-tab="ground_truth">Ground Truth</button>'
    ]
    panes = [
        f'<div class="tab-pane active" data-pane="ground_truth">'
        f'<div class="card-box provenance"><h3>Metadata</h3>{metadata_html(meta, p)}</div>'
        f'<h3>Model</h3>{code_block(p["model"], "python", copy_id=f"model-{idx}")}'
        f'</div>'
    ]
    for fw in FRAMEWORK_ORDER + [f for f in best if f not in FRAMEWORK_ORDER]:
        entry = best.get(fw)
        if entry is None:
            continue
        slug = fw.lower().replace(" ", "_")
        buttons.append(
            f'<button class="tab-btn" type="button" data-tab="{slug}">{esc(fw)}</button>'
        )
        panes.append(f'<div class="tab-pane" data-pane="{slug}">{generated_model_card(entry)}</div>')
    return (
        f'<div class="page-section"><h2>Models</h2>'
        f'<div class="tab-group"><div class="tab-bar">{"".join(buttons)}</div>'
        + "".join(panes)
        + "</div></div>"
    )


def build_problem_page(p: dict, meta: dict, idx: int, total: int, generated: dict) -> None:
    pid = p["id"]

    description_box = (
        f'<div class="card-box"><h3>Description</h3>'
        f'<div class="md-desc">{esc(p["description"])}</div></div>'
    )

    instances_html = instances_section_html(p, idx)

    gen_for_problem = generated.get(pid, {})

    prev_next = ""
    if total > 1:
        prev_next = '<div style="display:flex;justify-content:space-between;gap:10px;margin-top:30px">'
        prev_next += f'<a class="btn" href="{problems_list[idx - 1]["id"]}.html">← prev</a>' if idx > 0 else "<span></span>"
        prev_next += f'<a class="btn" href="{problems_list[idx + 1]["id"]}.html">next →</a>' if idx < total - 1 else "<span></span>"
        prev_next += "</div>"

    body = f"""
    <p class="breadcrumbs"><a href="index.html">problem</a> / {esc(pid)}</p>
    <h1 class="problem-title">{esc(pid)}</h1>

    {description_box}

    {instances_html}

    {models_section_html(p, meta, idx, gen_for_problem)}

    <div style="display:flex;gap:10px;margin-top:26px;flex-wrap:wrap">
      <a class="btn" href="{REPO_URL}/blob/main/dataset/{pid}/{pid}.cpmpy.py" target="_blank" rel="noopener">View original model (GitHub)</a>
      <a class="btn" href="{REPO_URL}/blob/main/dataset/{pid}/{pid}.json" target="_blank" rel="noopener">Instances JSON</a>
    </div>
    {prev_next}
    """

    (OUTPUT_DIR / "problems").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "problems" / f"{pid}.html").write_text(
        page(pid, "../", "problems", body, snippet(p["description"], 160)),
        encoding="utf-8",
    )


META_LABELS = {
    "source": "Source",
    "source_description": "Source description",
    "problem_instances": "Problem instances",
    "prompt": "Master prompt",
    "solver": "Solver",
    "solve_time": "Solve time (s)",
}


def humanize_key(key: str) -> str:
    return META_LABELS.get(key, key.replace("_", " ").capitalize())


def metadata_html(meta: dict, p: dict) -> str:
    rows = []
    for key, value in meta.items():
        if key in ("generated_by", "category", "timeout"):
            continue
        rows.append(f"<dt>{esc(humanize_key(key))}</dt><dd>{linkify(value)}</dd>")
    if meta.get("category"):
        rows.append(f"<dt>Category</dt><dd>{esc(meta['category'])}</dd>")
    rows.append(f"<dt>Origin</dt><dd>{esc(origin_label(p['origin']))}</dd>")
    return "<dl>" + "".join(rows) + "</dl>"


# --------------------------------------------------------------------------
# Framework view + Stats
# --------------------------------------------------------------------------

def build_frameworks(problems: list, stats: dict) -> None:
    by_fw = {}
    for p in problems:
        for fw in p["frameworks"]:
            by_fw.setdefault(fw, []).append(p)

    sections = []
    for fw in sorted(by_fw):
        items = "".join(
            f'<li><a href="problems/{p["id"]}.html">{esc(p["id"])}</a></li>'
            for p in by_fw[fw]
        )
        sections.append(
            f'<div class="section"><h2>{badge(fw, fw)} {stats["frameworks"][fw]} problems</h2>'
            f'<ul class="fw-list" style="columns:3;column-gap:24px;list-style:none;padding:0">{items}</ul></div>'
        )

    body = (
        '<p class="desc" style="margin-top:0">All problems with at least one model per framework.</p>'
        + "".join(sections)
    )
    (OUTPUT_DIR / "framework.html").write_text(
        page("Framework view", "", "frameworks", body), encoding="utf-8"
    )


def svg_hist(items: list, width: int = 760, height: int = 230, color: str = "#4f46e5") -> str:
    """Vertical bar histogram. items: list of (label, count)."""
    max_v = max(c for _, c in items) or 1
    pad_l, pad_b = 42, 36
    plot_w = width - pad_l - 12
    plot_h = height - pad_b - 12
    slot = plot_w / len(items)
    bar_w = slot * 0.5
    parts = [f'<svg viewBox="0 0 {width} {height}" width="100%" style="max-width:{width}px" role="img" aria-label="histogram">']
    for g in range(5):
        gy = pad_b + plot_h - g * plot_h / 4
        parts.append(f'<line x1="{pad_l}" y1="{gy:.1f}" x2="{width - 10}" y2="{gy:.1f}" stroke="#e5e7eb" stroke-width="1"/>')
        parts.append(
            f'<text x="{pad_l - 8}" y="{gy + 4:.1f}" text-anchor="end" font-size="11" fill="#6b7280">{int(round(g * max_v / 4))}</text>'
        )
    for i, (label, c) in enumerate(items):
        x = pad_l + i * slot + (slot - bar_w) / 2
        h = plot_h * c / max_v
        parts.append(f'<rect x="{x:.1f}" y="{pad_b + plot_h - h:.1f}" width="{bar_w:.1f}" height="{max(0, h):.1f}" rx="3" fill="{color}"/>')
        parts.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{pad_b + plot_h + 18}" text-anchor="middle" font-size="12" fill="#1f2430">{esc(label)}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def coverage_summary(problems: list, frameworks: list, stats: dict) -> str:
    pills = []
    for fw in frameworks:
        n = stats["frameworks"][fw]
        pct = 100.0 * n / max(1, stats["problems"])
        pills.append(
            f'<div class="stat"><div class="num">{n}<span style="font-size:1rem;color:var(--muted)"> ({pct:.0f}%)</span></div>'
            f'<div class="lbl">{esc(fw)} problems</div></div>'
        )
    multi = sum(1 for p in problems if len(p["frameworks"]) > 1)
    pills.append(
        f'<div class="stat"><div class="num">{multi}</div><div class="lbl">problems in multiple frameworks</div></div>'
    )
    return f'<div class="stat-row">{"".join(pills)}</div>'


def build_stats(problems: list, stats: dict, generated: dict) -> None:
    frameworks = sorted({fw for p in problems for fw in p["frameworks"]})
    origins = sorted(stats["origins"])

    buckets = [("0", 0, 1), ("1", 1, 2), ("2–5", 2, 6), ("6–20", 6, 21), ("21+", 21, None)]
    hist_items = []
    for label, lo, hi in buckets:
        if hi is None:
            count = sum(1 for p in problems if len(p["instances"]) >= lo)
        else:
            count = sum(1 for p in problems if lo <= len(p["instances"]) < hi)
        hist_items.append((label, count))
    hist_chart = svg_hist(hist_items)

    fw_rows = "".join(
        f'<tr><td>{esc(f)}</td><td class="num">{n}</td></tr>'
        for f, n in sorted(stats["frameworks"].items())
    )
    origin_rows = "".join(
        f'<tr><td>{esc(origin_label(o))}</td><td class="num">{n}</td></tr>'
        for o, n in sorted(stats["origins"].items())
    )
    top = sorted(problems, key=lambda p: -len(p["instances"]))[:10]
    top_rows = "".join(
        f'<tr><td class="mono"><a href="problems/{p["id"]}.html">{esc(p["id"])}</a></td>'
        f'<td class="num">{len(p["instances"])}</td></tr>'
        for p in top
    )

    # --- generated models stats ---
    gen_by_fw = {}
    gen_by_badge = {}
    gen_by_submission = {}
    for by_fw in generated.values():
        for fw, entries in by_fw.items():
            gen_by_fw[fw] = gen_by_fw.get(fw, 0) + len(entries)
            for e in entries:
                badge_key = e["metrics"].get("verdict", {}).get("badge", "unknown")
                gen_by_badge[badge_key] = gen_by_badge.get(badge_key, 0) + 1
                gen_by_submission[e["submission"]] = gen_by_submission.get(e["submission"], 0) + 1

    gen_fw_rows = "".join(
        f'<tr><td>{esc(f)}</td><td class="num">{n}</td></tr>'
        for f, n in sorted(gen_by_fw.items())
    )
    badge_items = []
    for key in VERDICT_STYLES:
        if key in gen_by_badge:
            color, label, _ = VERDICT_STYLES[key]
            badge_items.append((label, gen_by_badge[key], color))
    gen_badge_chart = ""
    if badge_items:
        max_v = max(c for _, c, _ in badge_items) or 1
        height = len(badge_items) * 34 + 14
        parts = [f'<svg viewBox="0 0 760 {height}" width="100%" style="max-width:760px" role="img" aria-label="generated model verdicts">']
        label_w = 240
        for i, (label, count, color) in enumerate(badge_items):
            y = 10 + i * 34
            bar_w = max(2, 460 * count / max_v)
            parts.append(f'<text x="{label_w - 10}" y="{y + 15}" text-anchor="end" font-size="13" fill="#1f2430">{esc(label)}</text>')
            parts.append(f'<rect x="{label_w}" y="{y}" width="{bar_w:.1f}" height="26" rx="4" fill="{color}"/>')
            parts.append(f'<text x="{label_w + bar_w + 8:.1f}" y="{y + 15}" font-size="12.5" fill="#6b7280">{count}</text>')
        parts.append("</svg>")
        gen_badge_chart = "".join(parts)
    gen_badge_rows = "".join(
        f'<tr><td>{esc(label)}</td><td class="num">{count}</td></tr>'
        for label, count, _ in badge_items
    )
    gen_sub_rows = "".join(
        f'<tr><td class="mono">{esc(s)}</td><td class="num">{n}</td></tr>'
        for s, n in sorted(gen_by_submission.items(), key=lambda kv: -kv[1])
    )

    body = f"""
    <div class="stat-row">
      <div class="stat"><div class="num">{stats["problems"]}</div><div class="lbl">problems</div></div>
      <div class="stat"><div class="num">{stats["instances"]}</div><div class="lbl">instances</div></div>
      <div class="stat"><div class="num">{stats["models"]}</div><div class="lbl">models</div></div>
      <div class="stat"><div class="num">{stats["generated_models"]}</div><div class="lbl">generated models</div></div>
      <div class="stat"><div class="num">{sum(1 for p in problems if p["instances"])}</div><div class="lbl">problems with instances</div></div>
    </div>
    <div class="section"><h2>Coverage</h2>
      {coverage_summary(problems, frameworks, stats)}
      <details>
        <summary>Per-problem matrix</summary>
        <div class="matrix-wrap">{coverage_matrix(problems, frameworks)}</div>
      </details></div>
    <div class="section"><h2>Instances per problem</h2>
      <p class="desc">How many problems have how many instances.</p>
      <div class="chart">{hist_chart}</div></div>
    <div class="section"><h2>Generated models</h2>
      <p class="desc">Models generated by AI agents/systems, from the CP-Bench leaderboard submissions.</p>
      <div class="chart">{gen_badge_chart}</div>
      <table class="plain"><thead><tr><th>Framework</th><th class="num">Generated models</th></tr></thead>
      <tbody>{gen_fw_rows}</tbody></table>
      <table class="plain" style="margin-top:12px"><thead><tr><th>Verdict</th><th class="num">Models</th></tr></thead>
      <tbody>{gen_badge_rows}</tbody></table>
      <table class="plain" style="margin-top:12px"><thead><tr><th>Submission</th><th class="num">Models</th></tr></thead>
      <tbody>{gen_sub_rows}</tbody></table></div>
    <div class="section"><h2>By framework</h2>
      <table class="plain"><thead><tr><th>Framework</th><th class="num">Problems</th></tr></thead>
      <tbody>{fw_rows}</tbody></table></div>
    <div class="section"><h2>By origin</h2>
      <table class="plain"><thead><tr><th>Origin</th><th class="num">Problems</th></tr></thead>
      <tbody>{origin_rows}</tbody></table></div>
    <div class="section"><h2>Top problems by number of instances</h2>
      <table class="plain"><thead><tr><th>Problem</th><th class="num">Instances</th></tr></thead>
      <tbody>{top_rows}</tbody></table></div>
    """
    (OUTPUT_DIR / "stats.html").write_text(
        page("Stats", "", "stats", body), encoding="utf-8"
    )


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

problems_list = []


def main() -> None:
    if not DATASET_JSONL.is_file():
        raise SystemExit(
            f"Missing {DATASET_JSONL}. Run `python jsonl_convert.py` first."
        )

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()
    shutil.copy2(WEB_SRC / "style.css", OUTPUT_DIR / "style.css")
    shutil.copy2(WEB_SRC / "app.js", OUTPUT_DIR / "app.js")

    problems = []
    with DATASET_JSONL.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            meta = parse_metadata(data.get("metadata", []))
            if data.get("framework"):
                frameworks = [data["framework"]]
            else:
                frameworks = detect_frameworks(data.get("model", ""))
            origin = meta.get("generated_by", "hand")
            problems.append(
                {
                    "id": data["id"],
                    "description": data.get("description", ""),
                    "model": data.get("model", ""),
                    "example_instance": data.get("example_instance", ""),
                    "instances": data.get("instances") or [],
                    "example_solution": data.get("example_solution", {}),
                    "decision_variables": data.get("decision_variables", []),
                    "frameworks": frameworks,
                    "category": meta.get("category", "other"),
                    "origin": origin,
                    "meta": meta,
                    "snippet": snippet(data.get("description", "")),
                }
            )

    global problems_list
    problems_list = problems

    generated = load_generated_models()
    gen_total = sum(len(v) for by_fw in generated.values() for v in by_fw.values())

    stats = {
        "problems": len(problems),
        "instances": sum(len(p["instances"]) for p in problems),
        "models": sum(len(p["frameworks"]) for p in problems),
        "generated_models": gen_total,
        "frameworks": {},
        "origins": {},
    }
    for p in problems:
        for fw in p["frameworks"]:
            stats["frameworks"][fw] = stats["frameworks"].get(fw, 0) + 1
        stats["origins"][p["origin"]] = stats["origins"].get(p["origin"], 0) + 1

    build_index(problems, stats)
    build_frameworks(problems, stats)
    build_stats(problems, stats, generated)
    for idx, p in enumerate(problems):
        build_problem_page(p, p["meta"], idx, len(problems), generated)

    # client-side index data (escaped so it can't break out of <script>)
    index_data = {
        "problems": [
            {
                "id": p["id"],
                "frameworks": p["frameworks"],
                "origin": p["origin"],
                "originLabel": origin_label(p["origin"]),
                "snippet": p["snippet"],
                "instances": len(p["instances"]),
                "generated": sum(len(v) for v in generated.get(p["id"], {}).values()),
            }
            for p in problems
        ]
    }
    js = "window.DCP_DATA = " + json.dumps(index_data, ensure_ascii=False).replace("<", "\\u003c") + ";\n"
    (OUTPUT_DIR / "data.js").write_text(js, encoding="utf-8")

    print(f"Generated {len(problems)} problem pages in {OUTPUT_DIR}")


if __name__ == "__main__":
    REPO_HEAD = repo_head_short()
    main()
