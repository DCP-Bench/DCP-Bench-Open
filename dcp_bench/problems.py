"""A problem's files, and an index over them.

    dataset/<problem>/
      description.md         the natural language description, in Markdown
      metadata.json          the facts below, for indexing and filtering
      <problem>.cpmpy.py     the reference: origin comments, data section, model
      <problem>.json         the instances

Each `# Key: value` comment at the top of a reference says where the problem came
from. metadata.json holds those as data, with what the reference itself establishes:
its objective, its declared outputs and its instance fields. `sync` writes the file,
keeping any other key added by hand, and the dataset audit checks that it is current.

    python -m dcp_bench.problems list --category csplib --objective minimize
    python -m dcp_bench.problems sync [PROBLEM ...]

Reading a description or metadata needs nothing but the standard library; only `sync`
loads the reference.
"""
import argparse
import json
import re
from pathlib import Path

DATASET = Path(__file__).resolve().parents[1] / "dataset"

OBJECTIVES = ("satisfaction", "minimize", "maximize")

# What each origin comment says a source provides. `origin` is where the problem was
# taken from, as a plain `# Source:` says; the others are more specific.
SOURCE_KINDS = {
    "source": ["origin"],
    "source description": ["description"],
    "description": ["description"],
    "source model": ["model"],
    "model source": ["model"],
    "example model": ["model"],
    "problem instances": ["instances"],
    "source and problem instances": ["origin", "instances"],
    "source description and problem instances": ["description", "instances"],
    "misc": ["note"],
}

_HEADER_LINE = re.compile(r"#\s*([A-Za-z][A-Za-z ]*?)\s*:\s*(.*)$")
_URL = re.compile(r"https?://\S+")


def description_path(folder):
    return Path(folder) / "description.md"


def metadata_path(folder):
    return Path(folder) / "metadata.json"


def read_description(folder):
    """The problem description, as a model is written from it."""
    return description_path(folder).read_text(encoding="utf-8").strip()


def read_metadata(folder):
    return json.loads(metadata_path(folder).read_text(encoding="utf-8"))


def reference_path(folder):
    folder = Path(folder)
    return folder / f"{folder.name}.cpmpy.py"


def _header_length(lines):
    """How many leading lines are the shebang and the `# Key: value` comments."""
    count = 0
    for line in lines:
        if not (line.startswith("#!") or _HEADER_LINE.fullmatch(line.strip())):
            break
        count += 1
    return count


def reference_body(source):
    """A reference without its origin comments: the data section and the model."""
    lines = source.splitlines(keepends=True)
    return "".join(lines[_header_length(lines):]).lstrip("\r\n")


def origin(source):
    """The origin comments as data: `category`, `sources`, and `name` and `timeout` if set.

    A comment whose key is not known is an error, so that a typo cannot quietly drop a
    source from the index.
    """
    lines = source.splitlines()
    fields, sources = {}, []
    for line in lines[:_header_length(lines)]:
        if line.startswith("#!"):
            continue
        key, value = _HEADER_LINE.fullmatch(line.strip()).groups()
        key, value = key.lower(), value.strip()
        if key in ("category", "name"):
            fields[key] = value
        elif key == "timeout":
            fields["timeout"] = int(value)
        elif key not in SOURCE_KINDS:
            raise ValueError(f"Unknown origin comment: {line.strip()}")
        elif value:
            form = "url" if _URL.fullmatch(value) else "text"
            sources += [{"kind": kind, form: value} for kind in SOURCE_KINDS[key]]
    return {**fields, "sources": sources}


def derived_metadata(folder):
    """What metadata.json must say, from the reference alone. Executes its model section."""
    from .reference import embedded_instance, load_reference

    folder = Path(folder)
    source = reference_path(folder).read_text(encoding="utf-8-sig")
    instance = embedded_instance(source)
    model, outputs = load_reference(source, instance)
    objective = "satisfaction"
    if model.has_objective():
        objective = "minimize" if getattr(model, "objective_is_min", True) else "maximize"
    return {"id": folder.name, **origin(source), "objective": objective,
            "outputs": list(outputs), "instance_fields": list(instance)}


def sync(folder):
    """Write metadata.json, keeping any key `derived_metadata` does not produce."""
    path = metadata_path(folder)
    existing = read_metadata(folder) if path.is_file() else {}
    derived = derived_metadata(folder)
    # `name` and `timeout` are optional, so a removed comment has to remove them here too.
    kept = {key: value for key, value in existing.items() if key not in {*derived, "name", "timeout"}}
    path.write_text(json.dumps({**derived, **kept}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def problems(dataset=DATASET, *, category=None, objective=None):
    """The metadata of each problem that matches, sorted by id."""
    found = (read_metadata(path.parent) for path in sorted(Path(dataset).glob("*/metadata.json")))
    return [meta for meta in found
            if (category is None or meta["category"] == category)
            and (objective is None or meta["objective"] == objective)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="print the ids of the problems that match")
    listing.add_argument("--category")
    listing.add_argument("--objective", choices=OBJECTIVES)
    listing.add_argument("--json", action="store_true", help="print the full metadata, one object per line")
    syncing = commands.add_parser("sync", help="write metadata.json, for every problem unless some are named")
    syncing.add_argument("problem", nargs="*")
    args = parser.parse_args(argv)
    if args.command == "list":
        for meta in problems(category=args.category, objective=args.objective):
            print(json.dumps(meta, ensure_ascii=False) if args.json else meta["id"])
    else:
        folders = [DATASET / name for name in args.problem] or sorted(p for p in DATASET.iterdir() if p.is_dir())
        for folder in folders:
            sync(folder)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
