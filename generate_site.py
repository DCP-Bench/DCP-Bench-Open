#!/usr/bin/env python3
"""Generate the static DCP Rosetta website from dcp-bench-open.jsonl.

Usage:
    python jsonl_convert.py   # optional, to refresh the jsonl from dataset/
    python generate_site.py

Output: site/ (build output, not committed; the deploy workflow regenerates it).
Requires only the Python standard library.
"""

import functools
import html
import json
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlparse

from evaluation.results import digest

DATASET_JSONL = Path("dcp-bench-open.jsonl")
WEB_SRC = Path("web")
OUTPUT_DIR = Path("site")
GENERATED_DIR = Path("generated_models")
FLAGS_PATH = Path("generation") / "flags.json"
SOLVERS_DIR = Path("solvers")

REPO_URL = "https://github.com/DCP-Bench/DCP-Bench-Open"
# Where the deploy workflow publishes site/: link previews need absolute URLs.
SITE_URL = "https://dcp-bench.github.io/DCP-Bench-Open/"

TITLE = "DCP Rosetta"
ASSET_VERSION = "catalogue-v43"
# Set by main() from the content of data.js.
DATA_VERSION = ""
SUBTITLE = (
    "A growing collection of <strong>D</strong>iscrete <strong>C</strong>ombinatorial "
    "<strong>P</strong>roblems, with models for a wide range of solvers and paradigms."
)
# The same sentence where markup cannot go: meta tags and link previews.
SUBTITLE_TEXT = re.sub(r"<[^>]+>", "", SUBTITLE)

# The collections in SOURCES.md, by the `category` each problem's metadata
# names: what a reader calls the collection, and where it lives.
SOURCE_COLLECTIONS = {
    "aplai_course": ("APLAI course", "https://github.com/kostis-init/CP-LLMs-ICL/tree/main/data/APLAI_course"),
    "complex_or": ("ComplexOR", "https://github.com/xzymustbexzy/Chain-of-Experts"),
    "cpmpy_examples": ("CPMpy examples", "https://github.com/CPMpy/cpmpy/tree/master/examples"),
    "csplib": ("CSPLib", "https://www.csplib.org/Problems/"),
    "hakan_examples": ("Hakan Kjellerstrand's CPMpy models", "https://github.com/hakank/hakank/tree/master/cpmpy"),
}

# A tab icon: the indigo of the header with the site's initials.
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='7' fill='%234f46e5'/%3E%3Ctext x='16' y='21' "
           "font-family='Arial,sans-serif' font-size='12' font-weight='700' text-anchor='middle' "
           "fill='white'%3EDCP%3C/text%3E%3C/svg%3E")

# What a model is written in, per `language` in solvers/<id>/metadata.yaml:
# the highlight.js grammar to ask for, and the label above the code block.
#
# The grammar is cosmetic and the label is the claim, so an approximation is
# only ever made in the first slot. highlight.js 11.9.0's bundle ships 36
# grammars: python and cpp are among them, prolog and julia are loaded separately below,
# and neither MiniZinc nor ASP has one anywhere. MiniZinc uses the small
# grammar in web/minizinc.js; ASP borrows Prolog's, whose surface it shares
# (% comments, :- rules, capitalised variables).
LANGUAGES = {
    "python": ("python", "Python"),
    "cpp": ("cpp", "C++"),
    "prolog": ("prolog", "Prolog"),
    "asp": ("prolog", "ASP"),
    "minizinc": ("minizinc", "MiniZinc"),
    # highlight.js 11.9.0 ships rust in the common bundle, so no extra grammar.
    "rust": ("rust", "Rust"),
    # No highlight.js grammar exists for Picat; Prolog's would misread its
    # `=>` rules and loop statements, so the model is shown uncoloured.
    "picat": ("plaintext", "Picat"),
    # julia is not in the common bundle either and is loaded like prolog.
    "julia": ("julia", "Julia"),
}

# Only for a model whose integration is no longer installed under solvers/.
EXTENSION_LANGUAGE = {".py": "python", ".cpp": "cpp", ".pl": "prolog",
                      ".lp": "asp", ".mzn": "minizinc", ".rs": "rust", ".pi": "picat", ".jl": "julia"}

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


URL_RE = re.compile(r"https?://[^\s<>\"]+")
HAKANK_URL = re.compile(r"https?://(?:www\.)?hakank\.org/([^\s\"'<>()]*)")


def mirrored(text: str) -> str:
    """Point hakank.org links at Hakan Kjellerstrand's GitHub repository.

    hakank.org stopped answering in October 2026. The repository holds the
    same files under the same paths; his blog posts have no copy there, so
    those links are left alone.
    """
    def swap(match):
        path = match.group(1).rstrip(".,;:")
        tail = match.group(1)[len(path):]
        if not path or path.startswith("constraint_programming_blog/"):
            return match.group(0)
        kind = "tree" if path.endswith("/") else "blob"
        return f"https://github.com/hakank/hakank/{kind}/master/{path}{tail}"
    return HAKANK_URL.sub(swap, text)


def url_end(url: str) -> int:
    """Where a URL found in prose ends: before a trailing comma or full stop,
    and before a closing parenthesis it did not open."""
    end = len(url)
    while end and (url[end - 1] in ".,;:!?'" or
                   (url[end - 1] == ")" and url.count("(", 0, end) < url.count(")", 0, end))):
        end -= 1
    return end


def linkify(text: str) -> str:
    """Escape text and wrap URLs in anchors."""
    out, last = [], 0
    text = mirrored(text)
    for match in URL_RE.finditer(text):
        url = match.group(0)[:url_end(match.group(0))]
        out.append(esc(text[last:match.start()]))
        out.append(f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(url)}</a>')
        last = match.start() + len(url)
    out.append(esc(text[last:]))
    return "".join(out)


# Math in a description, as app.js finds it: $$..$$, \[..\], \(..\), and
# $..$ only where it cannot be a price ("$20 and $5" stays text).
MATH_RE = re.compile(r"\$\$.+?\$\$|\\\[.+?\\\]|\\\(.+?\\\)|\$(?=[^\s\d$])[^$\n]*?[^\s$\\]\$(?!\d)", re.S)


def compact_json(value, indent: int = 0, width: int = 88) -> str:
    """JSON with each list of numbers or strings on one line, wrapped at
    `width`, so a row of data reads as a row; anything nested gets a line
    per item as json.dumps(indent=2) would give it."""
    pad = "  " * indent
    if isinstance(value, dict) and value:
        items = [f"{pad}  {json.dumps(key, ensure_ascii=False)}: {compact_json(item, indent + 1, width)}"
                 for key, item in value.items()]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(value, list) and value:
        if any(isinstance(item, (dict, list)) for item in value):
            items = [pad + "  " + compact_json(item, indent + 1, width) for item in value]
            return "[\n" + ",\n".join(items) + "\n" + pad + "]"
        parts = [json.dumps(item, ensure_ascii=False) for item in value]
        line = "[" + ", ".join(parts) + "]"
        if len(pad) + len(line) <= width:
            return line
        rows, row = [], []
        for part in parts:
            if row and len(pad) + 2 + len(", ".join(row + [part])) + 1 > width:
                rows.append(row)
                row = []
            row.append(part)
        rows.append(row)
        return "[\n" + ",\n".join(pad + "  " + ", ".join(r) for r in rows) + "\n" + pad + "]"
    return json.dumps(value, ensure_ascii=False)


MODEL_ID = re.compile(r"claude-(opus|sonnet|haiku)-(\d+)(?:-(\d{1,2})(?!\d))?")


def generated_by_label(raw: str) -> str:
    """The model that wrote a generated model, and the agent where the record
    names one. Records hold free-form notes beside them, such as
    "claude-opus-5 / model-generator campaign (100-model target)", which the
    page leaves out. A value naming no Claude model is shown as it is."""
    if not raw:
        return "Unknown"
    match = MODEL_ID.search(raw)
    if not match:
        return raw
    family, major, minor = match.groups()
    label = f"Claude {family.capitalize()} {major}" + (f".{minor}" if minor else "")
    if re.search(r"claude[- ]code", raw, re.I):
        label += " (Claude Code)"
    return label


def parse_metadata(metadata: list) -> dict:
    fields = {}
    for line in metadata:
        m = re.match(r"#\s*([A-Za-z][A-Za-z ]*?)\s*:\s*(.*)$", line.strip())
        if m:
            key = m.group(1).strip().lower().replace(" ", "_")
            fields[key] = m.group(2).strip()
    return fields


def reference_model_code(problem_id: str, fallback: str) -> str:
    """Load the runnable reference model body, omitting metadata and its description."""
    path = Path("dataset") / problem_id / f"{problem_id}.cpmpy.py"
    try:
        code = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return fallback
    description = re.search(r'""".*?"""|\'\'\'.*?\'\'\'', code, re.DOTALL)
    if description:
        code = code[description.end():].lstrip("\r\n")
    trailing_newline = "\n" if code.endswith("\n") else ""
    return "\n".join(line.rstrip() for line in code.splitlines()) + trailing_newline


def snippet(text: str, limit: int = 180) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


HLJS = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0"
KATEX = "https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9"


def page(title: str, prefix: str, active: str, body: str, description: str = "",
         hero_note: str = "", path: str = "", math: bool = False) -> str:
    """`hero_note` is a line of HTML shown under a problem page's title;
    `path` is the page's place under SITE_URL, for link previews; `math`
    loads KaTeX for a description that has formulas."""
    nav = []
    for key, label, href in (("index", "Problems", "index.html"), ("paradigms", "Solvers", "paradigms.html")):
        cls = ' class="active"' if active == key else ""
        nav.append(f'<a{cls} href="{prefix}{href}">{label}</a>')
    nav.append('<span class="spacer"></span>')
    nav.append(
        f'<a class="gh" href="{REPO_URL}" target="_blank" rel="noopener">'
        '<svg class="github-icon" viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="currentColor" d="M12 .5a12 12 0 0 0-3.79 23.39c.6.11.82-.26.82-.58v-2.04c-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.33-1.76-1.33-1.76-1.09-.75.08-.74.08-.74 1.2.08 1.84 1.23 1.84 1.23 1.07 1.83 2.8 1.3 3.48.99.11-.77.42-1.3.76-1.6-2.67-.3-5.47-1.34-5.47-5.93 0-1.31.47-2.38 1.23-3.22-.12-.3-.53-1.52.12-3.18 0 0 1-.32 3.3 1.23a11.5 11.5 0 0 1 6 0c2.29-1.55 3.29-1.23 3.29-1.23.65 1.66.24 2.88.12 3.18.77.84 1.23 1.91 1.23 3.22 0 4.6-2.8 5.62-5.48 5.92.43.37.81 1.1.81 2.22v3.29c0 .32.22.69.83.57A12 12 0 0 0 12 .5Z"/>'
        '</svg><span>GitHub</span></a>'
    )

    if active == "index":
        hero = (
            f'<div class="hero">'
            f'<h1>{TITLE}</h1><p>{SUBTITLE}</p></div>'
        )
    else:
        note = f'<p class="hero-note">{hero_note}</p>' if hero_note else ""
        # app.js points this at the catalogue as it was left, filters and all.
        crumb = (f'<a class="crumb" href="{prefix}index.html">&larr; All problems</a>'
                 if active == "problem" else "")
        hero = f'<div class="hero problem-hero">{crumb}<h1>{esc(title)}</h1>{note}</div>'

    full_title = TITLE if active == "index" else f"{title} · {TITLE}"
    preview = description or SUBTITLE_TEXT
    head = [
        f'<meta name="description" content="{esc(preview)}">',
        f'<meta property="og:title" content="{esc(full_title)}">',
        f'<meta property="og:description" content="{esc(preview)}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:url" content="{SITE_URL}{path}">',
        f'<meta property="og:image" content="{SITE_URL}og-image.png">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    # Each page loads only what it uses: code highlighting and Markdown on a
    # problem page, the catalogue data on the index.
    scripts = []
    if active == "problem":
        head.append(f'<link rel="stylesheet" href="{HLJS}/styles/github-dark.min.css">')
        scripts += [f"{HLJS}/highlight.min.js", f"{HLJS}/languages/prolog.min.js",
                    f"{HLJS}/languages/julia.min.js", f"{prefix}minizinc.js?v={ASSET_VERSION}",
                    "https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"]
        if math:
            head.append(f'<link rel="stylesheet" href="{KATEX}/katex.min.css">')
            scripts.append(f"{KATEX}/katex.min.js")
    if active == "index":
        scripts.append(f"{prefix}data.js?v={DATA_VERSION}")
    scripts.append(f"{prefix}app.js?v={ASSET_VERSION}")

    commit = f" &middot; commit <code>{esc(REPO_HEAD)}</code>" if REPO_HEAD else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<link rel="icon" href="{FAVICON}">
{chr(10).join(head)}
<script>document.documentElement.classList.add("js");</script>
<link rel="stylesheet" href="{prefix}style.css?v={ASSET_VERSION}">
</head>
<body>
<header><nav>{"".join(nav)}</nav>{hero}</header>
<main>{body}</main>
<footer>{TITLE} is part of <a href="{REPO_URL}" target="_blank" rel="noopener">DCP-Bench Open</a> &middot; <a href="{REPO_URL}/blob/main/LICENSE" target="_blank" rel="noopener">Apache-2.0</a>{commit}</footer>
{chr(10).join(f'<script src="{src}"></script>' for src in scripts)}
</body>
</html>
"""


def code_block(code: str, lang: str, copy_id: str = None, head_label: str = None,
               link: str = None) -> str:
    """`link` adds a "GitHub" link to the file beside the Copy button."""
    head = ""
    if copy_id:
        github = (f'<a class="code-link" href="{esc(link)}" target="_blank" rel="noopener">GitHub</a>'
                  if link else "")
        head = (
            f'<div class="code-head"><span>{esc(head_label or lang)}</span>'
            f'<span class="code-actions">{github}'
            f'<button type="button" data-copy="{copy_id}">Copy</button></span></div>'
        )
    return (
        f"{head}<pre class=\"code-block\"><code id=\"{copy_id}\" "
        f'class="language-{lang}">{esc(code)}</code></pre>'
    )


# --------------------------------------------------------------------------
# Generated models (from generated_models/)
# --------------------------------------------------------------------------

def load_flags() -> dict:
    """generation/flags.json by model directory: kept models that failed an
    instance added after they were accepted. A missing file flags nothing."""
    try:
        entries = json.loads(FLAGS_PATH.read_text(encoding="utf-8")).get("flags") or []
    except (OSError, ValueError, AttributeError):
        return {}
    out = {}
    for item in entries:
        if isinstance(item, dict) and item.get("model"):
            out.setdefault(item["model"], []).append(item)
    return out


def load_generated_models() -> dict:
    """Scan generated_models/<problem>/<solver>/<submission>/ -> {problem: {solver id: [entries]}}.

    Keyed on the integration id, never on its display name: the name is read
    from `solvers/<id>/metadata.yaml` at render time so renaming an integration
    is a one-line metadata edit, and two integrations sharing a display name
    cannot collapse into one group.
    """
    out = {}
    if not GENERATED_DIR.is_dir():
        return out
    flags = load_flags()
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
                record_path = sub_dir / "record.json"
                if not record_path.is_file():
                    continue
                try:
                    metrics = json.loads(record_path.read_text(encoding="utf-8"))
                except Exception:
                    continue
                model_file = metrics.get("model_file") or next(
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
                    "directory": fw_dir.name,
                    "metrics": metrics,
                    "model_file": model_file,
                    "code": code,
                    "flags": flags.get(sub_dir.as_posix(), []),
                })
            if entries:
                solver = entries[0]["metrics"].get("solver") or fw_dir.name
                by_fw[solver] = entries
        if by_fw:
            out[problem_dir.name] = by_fw
    return out


def model_language(metrics: dict, model_file: str) -> tuple:
    """(highlight.js grammar, label) for a generated model's code block.

    Read from the integration's declared `language`, so a new integration is
    labelled correctly the moment it declares one. The file extension is only
    consulted for a model whose integration has since been removed.
    """
    language = (INTEGRATIONS.get(metrics.get("solver")) or {}).get("language")
    if language not in LANGUAGES and model_file:
        language = EXTENSION_LANGUAGE.get(Path(model_file).suffix)
    return LANGUAGES.get(language, ("plaintext", language or "Model"))


def framework_name(solver_id: str) -> str:
    """What the catalogue calls an integration. Falls back to the id, which is
    what is left when a model outlives the integration that produced it."""
    return (INTEGRATIONS.get(solver_id) or {}).get("name") or solver_id


def verdict_badge(metrics: dict) -> str:
    key = normalize_badge(metrics)
    color, label, tooltip = VERDICT_STYLES.get(key, VERDICT_STYLES["unknown"])
    return (
        f'<span class="badge" style="background:{color}" title="{esc(tooltip)}">'
        f"{esc(label)}</span>"
    )


def flag_badge(flags: list, problem: str = "") -> str:
    """Mark a model that a later instance disproved, with what disproved it."""
    if not flags:
        return ""
    failures = "; ".join(
        f'{instance_label(item.get("instance"), problem, item.get("instance_hash"))[0]} '
        f'({item.get("reason")}, rechecked {item.get("recorded")})'
        for item in flags)
    return (
        ' <span class="badge" style="background:#9a3412" title="Accepted on the instances the '
        'problem had when it was evaluated, then rejected on one added since">'
        'fails a later instance</span>'
        f'<p class="desc eval-note">Rejected on {esc(failures)}.</p>'
    )


def normalize_badge(metrics: dict) -> str:
    """A satisfaction problem can never be 'valid and optimal': the objective
    check passes trivially, so re-label such verdicts as plain 'solution valid'."""
    badge = metrics.get("verdict", {}).get("badge", "unknown")
    if badge == "solution_valid_and_optimal" and not metrics.get("is_optimization"):
        return "solution_valid"
    return badge



@functools.cache
def row_positions(problem: str) -> dict:
    """The problem's current JSON rows, by the hash the evaluator records for each."""
    path = Path("dataset") / problem / f"{problem}.json"
    try:
        rows = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return {}
    return {digest(row): i for i, row in enumerate(rows)} if isinstance(rows, list) else {}


def instance_label(identifier, problem: str = "", instance_hash: str | None = None) -> tuple:
    """Name an evaluator instance the way the Instances section above does.

    That section numbers the problem's JSON rows from 1 and calls the first one
    the example; the corpus guarantees row 0 is exactly the embedded example. The
    evaluator identifies rows by their index at evaluation time, so json:k is
    Instance k+1 unless rows were removed since; the recorded hash then finds the
    row where it is now, or shows that it is gone. Rows that duplicate an earlier
    one are skipped entirely. Returns the label plus the raw identifier, which is
    worth a tooltip rather than space on the page: it only matters when replaying
    an evaluation.
    """
    text = str(identifier)
    if identifier == "example":
        return "Instance 1", text
    if text.startswith("json:"):
        try:
            index = int(text.split(':', 1)[1])
        except ValueError:
            return text, ""
        if instance_hash and problem:
            now = row_positions(problem).get(instance_hash)
            if now is None:
                return f"Instance {index + 1} (since removed)", text
            index = now
        return f"Instance {index + 1}", text
    return text, ""


def mebibytes(value) -> str:
    """2048 reads as 2 GiB; anything else stays in MiB."""
    if isinstance(value, int) and value >= 1024 and value % 1024 == 0:
        return f"{value // 1024}&thinsp;GiB"
    return f"{value}&thinsp;MiB"


def plural(count, word: str) -> str:
    return f"{count} {word}{'' if count == 1 else 's'}"


def evaluation_html(metrics: dict, flags: list, has_instances: bool = True) -> str:
    """The verdict, then one pill per instance in the numbering of the
    Instances section, then the limits; the per-instance table is folded.

    A problem without instances was checked once, on the data its
    description fixes, so it gets one line and no numbering.
    """
    head = (f'<div class="eval-head"><h3>Evaluation</h3>{verdict_badge(metrics)}'
            f'{flag_badge(flags, metrics.get("problem", ""))}</div>')
    record = metrics.get("evaluation") or {}
    instances = record.get("instances") or []
    if not instances:
        return f'<div class="card-box evaluation">{head}</div>'

    pills, rows = [], []
    for item in instances:
        label, raw = instance_label(item.get("id"), metrics.get("problem", ""), item.get("instance_hash"))
        received, checked = item.get("solutions_received"), item.get("solutions_checked")
        status = (item.get("runner_status") or {}).get("status") or "did not run"
        if item.get("accepted"):
            outcome, css = "accepted", "ok"
        elif item.get("skipped"):
            outcome, css = f"skipped, {item.get('reason', '')}", "skip"
        else:
            outcome, css = item.get("reason") or "failed", "fail"
        seconds = item.get("execution_wall_seconds")
        solve = "&ndash;" if seconds is None else f"{seconds:.1f}&thinsp;s"
        tip = f"{label}: {outcome}"
        if checked is not None:
            tip += f", {plural(checked, 'solution')} checked"
        if seconds is not None:
            tip += f", {seconds:.1f} s"
        pills.append(f'<span class="eval-pill {css}" title="{esc(tip)}">'
                     f'{esc(label.removeprefix("Instance "))}</span>')
        emitted = "" if received is None else f' title="{received} emitted"'
        rows.append(
            f'<tr><td class="cell-id" title="{esc(raw)}">{esc(label)}</td>'
            f'<td class="cell-cat {css}">{esc(outcome)}</td>'
            f'<td{emitted}>{"&ndash;" if checked is None else checked}</td>'
            f'<td>{esc(status)}</td><td>{solve}</td></tr>'
        )

    requested, limits = record.get("requested") or {}, record.get("limits") or {}
    budget = (f'{limits.get("execution_timeout")}&thinsp;s, {mebibytes(limits.get("memory_mb"))}, '
              f'{limits.get("cpus")}&thinsp;CPU.')

    if not has_instances and len(instances) == 1:
        item = instances[0]
        outcome = ("Accepted" if item.get("accepted")
                   else f"Rejected ({item.get('reason') or 'failed'})")
        summary = f"{outcome} on the data in the description"
        if item.get("solutions_checked") is not None:
            summary += f" &middot; {plural(item['solutions_checked'], 'solution')} checked"
        if item.get("execution_wall_seconds") is not None:
            summary += f" &middot; solved in {item['execution_wall_seconds']:.1f}&thinsp;s"
        return (
            f'<div class="card-box evaluation">{head}'
            f'<p class="eval-summary">{summary}</p>'
            f'<p class="desc eval-note">Up to {plural(requested.get("solution_limit"), "solution")}, {budget}</p></div>'
        )

    accepted = sum(1 for item in instances if item.get("accepted"))
    summary = f"Accepted on {accepted} of {plural(len(instances), 'instance')}"
    skipped = record.get("skipped_instances") or []
    if skipped:
        summary += f", {len(skipped)} skipped as inconclusive"
    if record.get("solutions_checked") is not None:
        summary += f" &middot; {plural(record['solutions_checked'], 'solution')} checked"
    bounds = f'Up to {plural(requested.get("solution_limit"), "solution")} per instance, {budget}'
    return (
        f'<div class="card-box evaluation">{head}'
        f'<p class="eval-summary">{summary}</p>'
        f'<div class="eval-pills">{"".join(pills)}</div>'
        f'<p class="desc eval-note">{bounds}</p>'
        '<details class="eval-details"><summary>Per-instance results</summary>'
        '<div class="matrix-wrap"><table class="matrix"><thead><tr><th>Instance</th><th>Outcome</th>'
        '<th>Solutions</th><th>Run</th><th>Solve</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div></details></div>'
    )


def generated_model_html(entry: dict, has_instances: bool = True) -> str:
    """A generated model: who made it and for what, how it was judged, the code."""
    metrics = entry["metrics"]
    generated_by = metrics.get("generated_by", {})
    uid = f"{metrics.get('problem', '')}-{entry['submission']}"

    rows = [f"<dt>Generated by</dt><dd>{esc(generated_by_label(generated_by.get('base_llm')))}</dd>"]
    if generated_by.get("dataset_version"):
        rows.append(
            f"<dt>Dataset version</dt><dd>{esc(generated_by['dataset_version'])}</dd>"
        )
    if metrics.get("solver"):
        rows.append(f'<dt>Solver</dt><dd>{solver_link(metrics["solver"], "../")}</dd>')
    chips = paradigm_chips(metrics.get("solver"), "../")
    if chips:
        rows.append(f"<dt>Paradigm</dt><dd>{chips}</dd>")

    if entry["model_file"]:
        lang, label = model_language(metrics, entry["model_file"])
        link = (f'{REPO_URL}/blob/main/generated_models/{metrics.get("problem", "")}/'
                f'{entry["directory"]}/{entry["submission"]}/{entry["model_file"]}')
        model = code_block(entry["code"], lang, copy_id=f"gmod-{uid}", head_label=label, link=link)
    else:
        model = '<p class="desc">Code file not found.</p>'

    return (
        f'<div class="model-info"><div class="card-box provenance"><h3>Metadata</h3><dl>{"".join(rows)}</dl></div>'
        f'{evaluation_html(metrics, entry.get("flags"), has_instances)}</div>'
        f'<h3>Model</h3>{model}'
    )


VALID_BADGE_ORDER = [
    "solution_valid_and_optimal",
    "solution_valid_objective_unknown",
    "solution_valid",
    "solution_valid_not_optimal",
]


def select_best_generated(gen_by_fw: dict) -> dict:
    """Keep at most one generated model per framework: the best valid one
    (valid + optimal preferred for optimisation problems), and one no later
    instance has disproved over one that a later instance has. Frameworks
    without a valid model are dropped."""
    out = {}
    for fw, entries in gen_by_fw.items():
        best, best_rank = None, None
        for entry in entries:
            metrics = entry["metrics"]
            badge = normalize_badge(metrics)
            if badge in VALID_BADGE_ORDER:
                rank = (bool(entry.get("flags")), VALID_BADGE_ORDER.index(badge))
                if best is None or rank < best_rank:
                    best, best_rank = entry, rank
        if best is not None:
            out[fw] = best
    return out


# --------------------------------------------------------------------------
# Paradigms (solvers/paradigms.json + solvers/*/metadata.yaml)
# --------------------------------------------------------------------------

# Filled in by main(); the per-model renderers need them and threading them
# through every call site would say less than it costs.
INTEGRATIONS = {}
PARADIGM_NAMES = {}
PARADIGM_ABBREVS = {}
# Paradigm IDs in the order the Solvers page lists them.
PARADIGM_ORDER = []


def load_paradigm_vocabulary() -> list:
    """The controlled list of paradigm tags, in the order they are documented."""
    try:
        return json.loads((SOLVERS_DIR / "paradigms.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def load_integrations() -> dict:
    """Solver integrations by ID. The metadata files are JSON despite the suffix."""
    out = {}
    for path in sorted(SOLVERS_DIR.glob("*/metadata.yaml")):
        try:
            out[path.parent.name] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
    return out


def verified_models(generated: dict, integrations: dict):
    """Yield (problem, integration ID, entry) for the models this repository
    verified itself.

    A model only counts once its own evaluator accepted it and it names an
    integration still installed under `solvers/`; a paradigm read off anything
    else would be a guess. A flagged model does not count: an instance added
    after it was accepted disproved it.
    """
    for problem, by_framework in generated.items():
        for entries in by_framework.values():
            for entry in entries:
                metrics = entry["metrics"]
                solver = metrics.get("solver")
                if (metrics.get("verdict_source") == "container_evaluator" and solver in integrations
                        and not entry.get("flags")):
                    yield problem, solver, entry


# Paradigms that can only express one kind of problem: SAT has no objective,
# so a model of an optimisation problem does not count towards it.
PARADIGM_SCOPE = {"sat": "satisfaction"}
SCOPE_NOTES = {"sat": "SAT counts satisfaction problems only, as it has no objective function."}


def paradigm_breakdown(generated: dict, integrations: dict, vocabulary: list,
                       problem_types: dict | None = None, scopes: dict = PARADIGM_SCOPE) -> dict:
    """Group verified models and the problems they cover by paradigm.

    An integration may declare several paradigms, and then counts towards each
    one, so the per-paradigm totals deliberately do not sum to the overall
    total. Given each problem's type, a paradigm in `scopes` counts only the
    problems of the kind it can express. A tag
    outside the vocabulary is still reported rather than dropped —
    `tests/test_solvers.py` is what keeps one from appearing in the first place.
    """
    entries = {item["id"]: dict(item) for item in vocabulary}
    models = {tag: 0 for tag in entries}
    problems = {tag: set() for tag in entries}
    integration_models = {}
    integration_problems = {}
    by_paradigm = {}
    per_problem = {}

    # A problem one integration has several accepted models for counts once:
    # what is measured is how many problems each integration models.
    pairs = {(problem, solver) for problem, solver, _entry in verified_models(generated, integrations)}
    for problem, solver in sorted(pairs):
        integration_models[solver] = integration_models.get(solver, 0) + 1
        integration_problems.setdefault(solver, set()).add(problem)
        kind = (problem_types or {}).get(problem)
        for tag in integrations[solver].get("paradigms") or []:
            if kind and tag in scopes and scopes[tag] != kind:
                continue
            by_paradigm.setdefault(tag, {}).setdefault(solver, set()).add(problem)
            if tag not in entries:
                entries[tag] = {"id": tag, "name": tag, "summary":
                                "Not described in solvers/paradigms.json."}
                models[tag], problems[tag] = 0, set()
            models[tag] += 1
            problems[tag].add(problem)
            per_problem.setdefault(problem, set()).add(tag)

    for tag, item in entries.items():
        item["models"] = models[tag]
        item["problems"] = problems[tag]
        item["integrations"] = sorted(
            solver for solver, metadata in integrations.items()
            if tag in (metadata.get("paradigms") or [])
        )
    # Ties keep the order paradigms.json documents them in.
    order = {item["id"]: i for i, item in enumerate(vocabulary)}
    ranked = sorted(entries.values(),
                    key=lambda item: (-len(item["problems"]), order.get(item["id"], len(order)), item["id"]))
    return {
        "paradigms": ranked,
        "per_problem": {problem: sorted(tags) for problem, tags in per_problem.items()},
        "integration_models": integration_models,
        "integration_problems": {k: len(v) for k, v in integration_problems.items()},
        # Problems per integration within one paradigm, after scoping.
        "by_paradigm": {tag: {solver: len(found) for solver, found in solvers.items()}
                        for tag, solvers in by_paradigm.items()},
        "covered": by_paradigm,
    }


def model_paradigm(solver_id: str, problem_type: str) -> str:
    """The paradigm a model of a problem is written in: the first one its
    integration declares that can express the problem's type. PySAT models a
    satisfaction problem as SAT and an optimisation problem as MaxSAT."""
    tags = (INTEGRATIONS.get(solver_id) or {}).get("paradigms") or []
    for tag in tags:
        if PARADIGM_SCOPE.get(tag, problem_type) == problem_type:
            return tag
    return tags[0] if tags else ""


def paradigm_chips(solver_id: str, prefix: str) -> str:
    """The paradigms an integration declares, linked to their description."""
    metadata = INTEGRATIONS.get(solver_id) or {}
    links = [
        f'<a href="{prefix}paradigms.html#{esc(tag)}">{esc(PARADIGM_NAMES.get(tag, tag))}</a>'
        for tag in metadata.get("paradigms") or []
    ]
    return " &middot; ".join(links)


def solver_link(solver_id: str, prefix: str) -> str:
    """An integration's display name, linked to its row in the paradigm table
    that `build_paradigms` writes."""
    metadata = INTEGRATIONS.get(solver_id)
    if not metadata:
        return esc(solver_id)
    name = metadata.get("name", solver_id)
    return (f'<a href="{prefix}paradigms.html#solver-{esc(solver_id)}">'
            f'{esc(name)}</a>')


# What `solver` in metadata.yaml names, as a reader would recognise it. An
# integration missing here shows its raw value.
BACKEND_NAMES = {
    "choco": "Choco",
    "clasp": "clasp",
    "ortools": "OR-Tools CP-SAT",
    "cp_sat": "CP-SAT",
    "cplex": "CPLEX",
    "exact": "Exact",
    "gurobi": "Gurobi",
    "evalmaxsat": "EvalMaxSAT",
    "highs": "HiGHS",
    "gecode": "Gecode",
    # Picat and SWI-Prolog solve with their own libraries: nothing to add.
    "cp, sat": "",
    "cbc": "CBC",
    "pumpkin": "Pumpkin",
    "glucose42, RC2": "Glucose 4.2 (SAT), RC2 (MaxSAT)",
    "clpfd": "",
    "z3": "Z3",
}

# Where one paradigm row sees only part of an integration's backends. PySAT's
# satisfaction models, the only ones the SAT row counts, all run on Glucose.
BACKEND_BY_PARADIGM = {("pysat", "sat"): "Glucose 4.2"}


def backend_label(solver: str, paradigm: str = "") -> str:
    """The solver a framework hands its model to, when the name does not
    already say it: CPMpy runs OR-Tools CP-SAT, but PyChoco obviously runs Choco."""
    metadata = INTEGRATIONS.get(solver) or {}
    raw = metadata.get("solver", "")
    backend = BACKEND_BY_PARADIGM.get((solver, paradigm)) or BACKEND_NAMES.get(raw, raw)
    name = metadata.get("name", solver).lower()
    if not backend or backend.split(" (")[0].lower() in name:
        return ""
    return f'<span class="backend">{esc(backend)}</span>'


def missing_link(solver: str, missing: set, types: dict) -> str:
    """Opens the catalogue on the problems an integration has no model for.
    When they are all of one type, the link opens that type's tab."""
    if not missing:
        return ""
    kinds = {types[problem] for problem in missing}
    tab = f"&amp;type={next(iter(kinds))}" if len(kinds) == 1 else ""
    return (f'<a class="missing" href="index.html?framework={esc(solver)}&amp;modelled=no{tab}">'
            f'{len(missing)} not modelled</a>')


def paradigm_order(ranked: list) -> list:
    """Paradigms with the most integrations first, as the Solvers page lists
    them; ties keep the order paradigms.json documents them in."""
    order = list(PARADIGM_NAMES)
    return sorted(ranked, key=lambda item: (-len(item["integrations"]),
                                            order.index(item["id"]) if item["id"] in order else len(order)))


def browse_button(solver: str, count: int) -> str:
    """Opens the catalogue filtered to the problems one integration models;
    each problem there links straight to that integration's model."""
    if not count:
        return ""
    return f'<a class="browse" href="index.html?framework={esc(solver)}">Browse<span class="browse-long"> models</span> &rarr;</a>'


def coverage_count(count, total: int) -> str:
    """`163 / 164`: the count reads first, the catalogue size stays quiet."""
    return f'<span class="count">{count}</span><span class="of"> / {total}</span>'


def info_tip(tip_id: str, label: str, text: str) -> str:
    """A small "i" that shows `text` on hover or keyboard focus."""
    return (
        f'<span class="info-wrap"><span class="info" tabindex="0" role="button" '
        f'aria-label="About {esc(label)}" aria-describedby="{tip_id}">i</span>'
        f'<span class="tip" role="tooltip" id="{tip_id}">{esc(text)}</span></span>'
    )


def build_paradigms(problems: list, breakdown: dict) -> None:
    """One table: a row per paradigm, expanding to the integrations behind it."""
    ranked = breakdown["paradigms"]
    integration_problems = breakdown["integration_problems"]

    types = {p["id"]: p["type"] for p in problems}
    type_counts = {kind: sum(1 for t in types.values() if t == kind) for kind in set(types.values())}

    by_solvers = paradigm_order(ranked)

    groups, notes = [], []
    anchored: set = set()
    for item in by_solvers:
        tag = item["id"]
        scope = PARADIGM_SCOPE.get(tag)
        denominator = type_counts.get(scope, 0) if scope else len(types)
        in_scope = {problem for problem, kind in types.items() if not scope or kind == scope}
        covered = breakdown["covered"].get(tag, {})
        found = breakdown["by_paradigm"].get(tag, {})
        # The solvers that model the most problems in this paradigm lead;
        # ties read alphabetically by display name.
        solvers = sorted(item["integrations"], key=lambda solver: (
            -found.get(solver, 0), INTEGRATIONS[solver].get("name", solver).lower()))
        counts = [found.get(solver, 0) for solver in solvers]

        mark = ""
        if tag in SCOPE_NOTES:
            mark = f'<a class="note-mark" href="#note-{esc(tag)}" aria-label="Note on {esc(item["name"])}">*</a>'
            notes.append(f'<p class="table-note" id="note-{esc(tag)}">* {esc(SCOPE_NOTES[tag])}</p>')

        entries = []
        for solver in solvers:
            # A solver listed under two paradigms keeps its anchor on the first.
            anchor = "" if solver in anchored else f' id="solver-{esc(solver)}"'
            anchored.add(solver)
            entries.append(
                f'<li{anchor}><span class="solver-name">{esc(INTEGRATIONS[solver].get("name", solver))}'
                f'{backend_label(solver, tag)}</span>'
                f'<span class="solver-count">{coverage_count(found.get(solver, 0), denominator)}'
                f'{missing_link(solver, in_scope - covered.get(solver, set()), types)}</span>'
                f'{browse_button(solver, integration_problems.get(solver, 0))}</li>'
            )

        average = sum(counts) / len(counts) if counts else 0
        # One decimal, half up: 161.25 is 161.3, not the 161.2 binary floats give.
        tenths = int(average * 10 + 0.5)
        shown = str(tenths // 10) if tenths % 10 == 0 else f"{tenths // 10}.{tenths % 10}"
        # The count, then a Show/Hide button; the CSS writes the button's
        # word from aria-expanded, so the two cannot disagree.
        toggle = f'<span class="count">{len(solvers)}</span>' + (
            f'<button type="button" class="row-toggle" aria-expanded="false" '
            f'aria-label="Show the {len(solvers)} solvers for {esc(item["name"])}"></button>'
            if solvers else ""
        )
        head = (
            f'<tr class="paradigm-row"><td class="abbrev">{esc(item.get("abbrev", tag))}</td>'
            f'<td>{esc(item["name"])}{mark}'
            f'{info_tip("tip-" + esc(tag), item["name"], item.get("summary", ""))}</td>'
            f'<td class="num">{toggle}</td>'
            f'<td class="num">{coverage_count(shown, denominator)}</td></tr>'
        )
        # The solvers sit in one full-width row of their own, so their layout
        # does not depend on the paradigm columns above them.
        panel = (f'<tr class="solver-panel"><td colspan="4"><ul class="solver-list">{"".join(entries)}</ul></td></tr>'
                 if entries else "")
        groups.append(f'<tbody class="paradigm collapsed" id="{esc(tag)}">{head}{panel}</tbody>')

    body = f"""
    <div class="section"><div class="section-head"><h2>Coverage by paradigm</h2>
      <button type="button" class="btn expand-all" aria-pressed="false">Show all</button></div>
      <table class="plain paradigm-table"><thead><tr><th>Abbrev.</th><th>Name</th>
      <th class="num">Solvers</th><th class="num">Avg. problems</th></tr></thead>{"".join(groups)}</table>
      {"".join(notes)}
    </div>
    """
    (OUTPUT_DIR / "paradigms.html").write_text(
        page("Solvers", "", "paradigms", body,
             "How DCP Rosetta's verified models break down by modelling paradigm and solver.",
             path="paradigms.html"),
        encoding="utf-8",
    )


# --------------------------------------------------------------------------
# Index page (Problem view)
# --------------------------------------------------------------------------

IS_OPT_RE = re.compile(r"\b(minimize|maximize)\s*\(")


def source_group(meta: dict) -> str:
    """Return the dataset's original source/category identifier."""
    return meta.get("category") or "unclassified"


# --------------------------------------------------------------------------
# Problem pages
# --------------------------------------------------------------------------


def build_index(problems: list, generated: dict, breakdown: dict) -> None:
    """The problem catalogue: the filters, then a tab per problem type."""
    paradigm_options = "".join(
        f'<label><input type="checkbox" data-filter-group="paradigm" value="{esc(item["id"])}">'
        f'{esc(item["name"])}</label>'
        for item in breakdown["paradigms"] if item["problems"]
    )
    generated_frameworks = sorted(
        {
            framework
            for models in generated.values()
            for framework in select_best_generated(models)
        }
    )
    framework_options = "".join(
        f'<label><input type="checkbox" data-filter-group="framework" value="{esc(framework)}">'
        f'{esc(framework_name(framework))}</label>'
        for framework in sorted(generated_frameworks,
                                key=lambda s: framework_name(s).casefold())
    )
    body = f"""
    <div class="controls" aria-label="Problem filters">
      <label class="search-field"><span class="sr-only">Search problems</span>
        <input type="search" id="filter-q" placeholder="Search names and descriptions" autocomplete="off">
      </label>
      <div class="filter-menu" data-filter-menu="instances">
        <button type="button" class="filter-trigger" id="filter-instances" aria-expanded="false">Instances: All</button>
        <div class="filter-options" role="group" aria-label="Filter by instance count">
          <label><input type="checkbox" data-filter-group="instances" value="none">No instances</label>
          <label><input type="checkbox" data-filter-group="instances" value="single">Single</label>
          <label><input type="checkbox" data-filter-group="instances" value="multiple">Multiple</label>
        </div>
      </div>
      <div class="filter-menu" data-filter-menu="paradigm">
        <button type="button" class="filter-trigger" id="filter-paradigm" aria-expanded="false">Paradigm: All</button>
        <div class="filter-options" role="group" aria-label="Filter by modelling paradigm">
          {paradigm_options}
        </div>
      </div>
      <div class="filter-menu" data-filter-menu="framework">
        <button type="button" class="filter-trigger" id="filter-framework" aria-expanded="false">Solver: All</button>
        <div class="filter-options" role="group" aria-label="Filter by the solver of a generated model">
          {framework_options}
        </div>
      </div>
      <button type="button" id="reset-filters" class="reset-btn" disabled>Reset</button>
    </div>
    <div class="type-tabs">
      <div class="type-tab-list" role="tablist" aria-label="Problem type">
        <button type="button" class="type-tab active" role="tab" aria-selected="true" data-type="optimization"
          id="tab-optimization" aria-controls="panel-optimization">Optimization <span class="tab-count"></span></button>
        <button type="button" class="type-tab" role="tab" aria-selected="false" data-type="satisfaction"
          id="tab-satisfaction" aria-controls="panel-satisfaction">Satisfaction <span class="tab-count"></span></button>
      </div>
      <div class="results-side">
        <div class="mode-switch" role="group" aria-label="Problems the selected solvers" hidden>
          <button type="button" class="mode-btn active" data-mode="yes" aria-pressed="true">Modelled <span class="tab-count"></span></button>
          <button type="button" class="mode-btn" data-mode="no" aria-pressed="false">Not modelled <span class="tab-count"></span></button>
        </div>
        <p class="result-count" id="result-count"></p>
      </div>
    </div>
    <noscript><p class="empty-state">The catalogue needs JavaScript. The problems are also listed in
      <a href="{REPO_URL}/tree/main/dataset">the repository</a>.</p></noscript>
    <div class="problem-section" data-type="optimization" role="tabpanel" id="panel-optimization"
      aria-labelledby="tab-optimization"><div class="problem-table"></div></div>
    <div class="problem-section" data-type="satisfaction" role="tabpanel" id="panel-satisfaction"
      aria-labelledby="tab-satisfaction" hidden><div class="problem-table"></div></div>
    """
    (OUTPUT_DIR / "index.html").write_text(
        page("Problems", "", "index", body, SUBTITLE_TEXT), encoding="utf-8"
    )

def build_not_found() -> None:
    """GitHub Pages serves 404.html for any missing path, at any depth, so
    its links are absolute."""
    body = (f'<p>There is no page at this address. The catalogue lists every problem: '
            f'<a href="{SITE_URL}">{SITE_URL}</a></p>')
    (OUTPUT_DIR / "404.html").write_text(
        page("Page not found", SITE_URL, "missing", body, path="404.html"), encoding="utf-8")


def var_chips_short(vars_list: list) -> str:
    return "".join(f'<span class="chip">{esc(v)}</span>' for v in vars_list) or ""


def problem_instances(p: dict) -> list:
    """The instances a problem page shows. A problem without any has its data
    fixed in the description."""
    return p["instances"] or ([p["example_instance"]] if p["example_instance"] else [])


def instance_pane_html(inst, i: int, idx: int, active: bool, example_solution, decision_vars: list) -> str:
    """One instance's data, plus the example solution for instance 1."""
    pretty = compact_json(inst)
    data_pane = code_block(pretty, "json", copy_id=f"inst-{idx}-{i}", head_label=f"Instance {i} · JSON")
    buttons = '<button class="tab-btn active" type="button" data-tab="data">Data</button>'
    panes = f'<div class="tab-pane active" data-pane="data">{data_pane}</div>'
    if i == 1 and example_solution:
        sol_code = compact_json(example_solution)
        buttons += '<button class="tab-btn" type="button" data-tab="solution">Solution</button>'
        panes += (
            f'<div class="tab-pane" data-pane="solution">'
            f'<div class="chip-row">{var_chips_short(decision_vars)}</div>'
            f'{code_block(sol_code, "json", copy_id=f"sol-{idx}-{i}", head_label="Solution · JSON")}</div>'
        )
    inner = f'<div class="tab-group"><div class="tab-bar">{buttons}</div>{panes}</div>'
    if active is None:
        return inner
    state = " active" if active else ""
    return f'<div class="tab-pane{state}" data-pane="inst-{i}">{inner}</div>'


def instances_section_html(p: dict, idx: int) -> str:
    """A numbered picker over the instances, and the chosen one's data.

    The corpus guarantees instance 1 is the data the reference model has
    written into it, which is why only that one comes with a solution.
    """
    insts = problem_instances(p)
    if not insts:
        return ""
    solution, variables = p["example_solution"], p["decision_variables"]
    note = ('<p class="desc picker-note">Instance 1 is the data written into the reference model'
            + (", and the one shown with a solution." if solution else ".") + "</p>")
    if len(insts) == 1:
        body = note + instance_pane_html(insts[0], 1, idx, None, solution, variables)
    else:
        picks = "".join(
            f'<button class="tab-btn pick{" active" if i == 1 else ""}" type="button" '
            f'data-tab="inst-{i}" aria-label="Instance {i}">{i}</button>'
            for i in range(1, len(insts) + 1)
        )
        panes = "".join(instance_pane_html(inst, i, idx, i == 1, solution, variables)
                        for i, inst in enumerate(insts, 1))
        body = (f'<div class="tab-group picker-group"><div class="tab-bar picker" aria-label="Instances">'
                f'{picks}</div>{note}{panes}</div>')
    return (
        f'<details class="card-box instances-box">'
        f'<summary><h3>Instances <span class="count-note">({len(insts)})</span></h3></summary>'
        f'{body}</details>'
    )


def models_section_html(p: dict, meta: dict, idx: int, generated: dict) -> str:
    best = select_best_generated(generated)
    sources = sources_html(meta)
    reference = code_block(p["display_model"], "python", copy_id=f"model-{idx}", head_label="Python",
                           link=f"{REPO_URL}/blob/main/dataset/{p['id']}/{p['id']}.cpmpy.py")
    panes = [
        f'<div class="tab-pane active" data-pane="ground_truth">'
        + (f'<div class="card-box provenance"><h3>Sources</h3>{sources}</div>' if sources else "") +
        f'<h3>Model</h3>{reference}'
        f'</div>'
    ]
    # The generated models in one row per paradigm, in the Solvers page's
    # order, each row alphabetical.
    by_paradigm = {}
    for fw in sorted(best, key=lambda solver: framework_name(solver).casefold()):
        by_paradigm.setdefault(model_paradigm(fw, p["type"]), []).append(fw)
    rank = {tag: i for i, tag in enumerate(PARADIGM_ORDER)}
    rows = [
        '<div class="picker-row reference-row"><span class="picker-label" title="Written by hand; the ground '
        'truth every other model is checked against">Reference</span><div class="picker-chips">'
        '<button class="tab-btn pick active" type="button" data-tab="ground_truth">CPMpy (Python)</button>'
        '</div></div>'
    ]
    for tag in sorted(by_paradigm, key=lambda tag: (rank.get(tag, len(rank)), tag)):
        buttons = []
        for fw in by_paradigm[tag]:
            slug = fw.lower().replace(" ", "_")
            buttons.append(f'<button class="tab-btn pick" type="button" data-tab="{slug}">'
                           f'{esc(framework_name(fw))}</button>')
            panes.append(f'<div class="tab-pane" data-pane="{slug}">'
                         f'{generated_model_html(best[fw], bool(problem_instances(p)))}</div>')
        label = PARADIGM_ABBREVS.get(tag, tag) or "Other"
        rows.append(
            f'<div class="picker-row"><span class="picker-label" title="{esc(PARADIGM_NAMES.get(tag, label))}">'
            f'{esc(label)}</span><div class="picker-chips">{"".join(buttons)}</div></div>'
        )
    return (
        f'<div class="page-section"><h2>Models</h2>'
        f'<div class="tab-group model-group"><div class="tab-bar picker model-picker">{"".join(rows)}</div>'
        + "".join(panes)
        + "</div></div>"
    )


def source_html(category: str) -> str:
    """The collection a problem comes from, linked to it."""
    name, url = SOURCE_COLLECTIONS.get(category, (category, ""))
    if not url:
        return esc(name)
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(name)}</a>'


def build_problem_page(p: dict, meta: dict, idx: int, neighbours: tuple, generated: dict) -> None:
    """`neighbours` are the ids of the problems before and after this one in
    the catalogue's alphabetical order, or None at either end."""
    pid = p["id"]

    description_box = (
        f'<div class="card-box"><h3>Description</h3>'
        f'<div class="md-desc">{esc(p["description"])}</div></div>'
    )

    instances_html = instances_section_html(p, idx)
    # A puzzle whose numbers are all fixed carries no instances, so the footer
    # line must not claim there are some.
    shown_above = ("The reference model and the instances are"
                   if instances_html else "The reference model is")

    gen_for_problem = generated.get(pid, {})

    before, after = neighbours
    prev_next = ""
    if before or after:
        prev_next = '<div class="pager">'
        prev_next += (f'<a class="btn" href="{esc(before)}.html" rel="prev">&larr; {esc(before)}</a>'
                      if before else "<span></span>")
        prev_next += (f'<a class="btn" href="{esc(after)}.html" rel="next">{esc(after)} &rarr;</a>'
                      if after else "<span></span>")
        prev_next += "</div>"

    body = f"""
    {description_box}

    {instances_html}

    {models_section_html(p, meta, idx, gen_for_problem)}

    <p class="desc" style="margin-top:26px">{shown_above} shown above;
      the files live in
      <a href="{REPO_URL}/tree/main/dataset/{pid}" target="_blank" rel="noopener">dataset/{pid}</a>.</p>
    {prev_next}
    """

    (OUTPUT_DIR / "problems").mkdir(parents=True, exist_ok=True)
    kind = "Optimization" if p["type"] == "optimization" else "Satisfaction"
    hero_note = f'{kind} problem · Source: {source_html(p["source"])}'
    rendered_page = page(pid, "../", "problem", body, snippet(p["description"], 160), hero_note,
                         path=f"problems/{pid}.html", math=bool(MATH_RE.search(p["description"])))
    rendered_page = "\n".join(line.rstrip() for line in rendered_page.splitlines()) + "\n"
    (OUTPUT_DIR / "problems" / f"{pid}.html").write_text(
        rendered_page,
        encoding="utf-8",
    )


# Metadata that is not a source of the problem: the collection shows in the
# page header, `name` is the problem's title.
NOT_SOURCES = ("generated_by", "category", "problem_instances", "timeout", "name")


def link_text(url: str) -> str:
    """Name a link by where it goes: "GitHub · hakank/hakank · cabling.py",
    "csplib.org · prob006"."""
    parts = urlparse(url)
    host = parts.netloc.removeprefix("www.")
    segments = [unquote(segment) for segment in parts.path.split("/") if segment]
    if host == "github.com" and len(segments) >= 2:
        return " · ".join(["GitHub", f"{segments[0]}/{segments[1]}"] + segments[-1:][: len(segments) > 2])
    page = segments[-1] if segments else ""
    if host.endswith("wikipedia.org"):
        page = page.replace("_", " ")
    return f"{host} · {page}" if page else host


def sources_html(meta: dict) -> str:
    """The reference model's sources as one list: each bare URL as a link
    named by its site and page, each citation or note as written.

    The metadata keys are left out. They vary from file to file
    (source_model, model_source, source_and_problem_instances, ...) and
    say less than the links themselves.
    """
    items, seen = [], set()
    for key, value in meta.items():
        value = mirrored(value.strip())
        if key in NOT_SOURCES or not value:
            continue
        if URL_RE.fullmatch(value) and url_end(value) == len(value):
            if value not in seen:
                seen.add(value)
                items.append(f'<li><a href="{esc(value)}" target="_blank" rel="noopener" '
                             f'title="{esc(value)}">{esc(link_text(value))}</a></li>')
        else:
            items.append(f"<li>{linkify(value)}</li>")
    return f'<ul class="source-list">{"".join(items)}</ul>' if items else ""


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

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
    shutil.copy2(WEB_SRC / "minizinc.js", OUTPUT_DIR / "minizinc.js")
    shutil.copy2(WEB_SRC / "og-image.png", OUTPUT_DIR / "og-image.png")

    problems = []
    with DATASET_JSONL.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            meta = parse_metadata(data.get("metadata", []))
            problems.append(
                {
                    "id": data["id"],
                    "description": mirrored(data.get("description", "")),
                    "display_model": reference_model_code(data["id"], data.get("model", "")),
                    "example_instance": data.get("example_instance", ""),
                    "instances": data.get("instances") or [],
                    "example_solution": data.get("example_solution", {}),
                    "decision_variables": data.get("decision_variables", []),
                    "source": source_group(meta),
                    "type": "optimization" if IS_OPT_RE.search(data.get("model", "")) else "satisfaction",
                    "meta": meta,
                    "snippet": snippet(mirrored(data.get("description", ""))),
                }
            )

    generated = load_generated_models()

    global INTEGRATIONS, PARADIGM_NAMES, PARADIGM_ABBREVS, PARADIGM_ORDER
    INTEGRATIONS = load_integrations()
    vocabulary = load_paradigm_vocabulary()
    PARADIGM_NAMES = {item["id"]: item["name"] for item in vocabulary}
    PARADIGM_ABBREVS = {item["id"]: item.get("abbrev", item["id"]) for item in vocabulary}
    breakdown = paradigm_breakdown(generated, INTEGRATIONS, vocabulary,
                                   problem_types={p["id"]: p["type"] for p in problems})
    PARADIGM_ORDER = [item["id"] for item in paradigm_order(breakdown["paradigms"])]

    # client-side index data (escaped so it can't break out of <script>)
    index_data = {
        "problems": [
            {
                "id": p["id"],
                "type": p["type"],
                "snippet": p["snippet"],
                "text": " ".join(p["description"].split()),
                "instances": len(problem_instances(p)),
                "generatedFrameworks": sorted(select_best_generated(generated.get(p["id"], {})).keys()),
                "paradigms": breakdown["per_problem"].get(p["id"], []),
            }
            for p in problems
        ]
    }
    js = "window.DCP_DATA = " + json.dumps(index_data, ensure_ascii=False).replace("<", "\\u003c") + ";\n"
    (OUTPUT_DIR / "data.js").write_text(js, encoding="utf-8")
    # The pages ask for data.js by its content, so a rebuilt catalogue is
    # fetched again rather than served from a browser's cache.
    global DATA_VERSION
    DATA_VERSION = digest(js.encode())[:12]

    build_index(problems, generated, breakdown)
    build_not_found()
    build_paradigms(problems, breakdown)
    # prev/next walk the problems alphabetically, as the catalogue lists them.
    order = sorted(p["id"] for p in problems)
    for idx, p in enumerate(problems):
        at = order.index(p["id"])
        neighbours = (order[at - 1] if at > 0 else None,
                      order[at + 1] if at + 1 < len(order) else None)
        build_problem_page(p, p["meta"], idx, neighbours, generated)

    print(f"Generated {len(problems)} problem pages in {OUTPUT_DIR}")


if __name__ == "__main__":
    REPO_HEAD = repo_head_short()
    main()
