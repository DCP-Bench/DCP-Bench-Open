"""Build a site of redirect pages from the old catalogue URL to DCP Rosetta.

Usage: python .github/redirect_site.py DATASET_DIR OUTPUT_DIR

Writes one page per old page (index, paradigms, one per problem) plus a 404
page for anything else. Each page sends the browser to the same path under the
new site, keeping the query string and fragment, so links such as
index.html?framework=choco_python still land where they pointed.
"""
import html
import sys
from pathlib import Path

OLD = "/DCP-Bench-Open/"
NEW = "https://dcp-bench.github.io/DCP-Rosetta/"

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>DCP Rosetta has moved</title>
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={target}">
<script>
var i = location.pathname.indexOf("{old}");
var rest = i < 0 ? "" : location.pathname.slice(i + {old_len});
location.replace("{new}" + rest + location.search + location.hash);
</script>
</head>
<body>
<p>The catalogue has moved to <a href="{target}">{target}</a>.</p>
</body>
</html>
"""


def page(path: str) -> str:
    target = html.escape(NEW + path)
    return PAGE.format(target=target, old=OLD, old_len=len(OLD), new=NEW)


def main(dataset: str, output: str) -> None:
    out = Path(output)
    (out / "problems").mkdir(parents=True, exist_ok=True)
    pages = ["index.html", "paradigms.html"]
    pages += [f"problems/{p.parent.name}.html" for p in sorted(Path(dataset).glob("*/*.cpmpy.py"))]
    for path in pages:
        (out / path).write_text(page(path), encoding="utf-8")
    # Any other old path: the script maps it; without script, the root.
    (out / "404.html").write_text(page(""), encoding="utf-8")
    print(f"Wrote {len(pages) + 1} redirect pages to {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
