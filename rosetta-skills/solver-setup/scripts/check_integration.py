"""Check a solver integration against references/integration.md.

Usage, from the DCP-Bench Open repository root:

    python <skill>/scripts/check_integration.py ID [--static] [--repo PATH]

Prints one line per check (PASS, WARN or FAIL) and exits 1 if any check failed.
Without --static it also verifies solvers/ID/readiness.json against the current
files and image, which needs Docker; use --static while the work is in progress.
It checks what can be checked without running the integration: whether run.py
is honest is for readiness_test.py to show, not for this script.
"""
import argparse
import ast
import json
from pathlib import Path
import re
import sys

REQUIRED_KEYS = {"id", "name", "language", "framework", "solver", "paradigms", "image",
                 "extension", "enumeration", "protocol_version"}
OPTIONAL_KEYS = {"optimization", "compilation", "instance_binding"}
BINDINGS = {"any", "rectangular_uniform", "reshaped"}
FILES = ("metadata.yaml", "Dockerfile", "run.py", "readiness_test.py")

results = []


def report(status, name, detail=""):
    results.append(status)
    print(f"{status:4}  {name}" + (f": {detail}" if detail else ""))


def check(name, ok, detail="", warn=False):
    report("PASS" if ok else ("WARN" if warn else "FAIL"), name, "" if ok else detail)
    return ok


def literal_dict_keys(path, variable):
    """Keys of a module-level dict literal, read without importing the module."""
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if (isinstance(node, ast.Assign) and any(getattr(t, "id", None) == variable for t in node.targets)
                and isinstance(node.value, ast.Dict)):
            return {ast.literal_eval(key) for key in node.value.keys}
    return set()


def check_metadata(root, solver_id, metadata):
    keys = set(metadata)
    check("metadata: required keys", REQUIRED_KEYS <= keys, f"missing {sorted(REQUIRED_KEYS - keys)}")
    check("metadata: no unknown keys", keys <= REQUIRED_KEYS | OPTIONAL_KEYS,
          f"unknown {sorted(keys - REQUIRED_KEYS - OPTIONAL_KEYS)}")
    check("metadata: id matches folder", metadata.get("id") == solver_id,
          f"id {metadata.get('id')!r} in solvers/{solver_id}/")
    check("metadata: id format", re.fullmatch(r"[a-z0-9_]+", solver_id or "") is not None,
          "lowercase letters, digits and underscores only")
    for key in ("name", "language", "framework", "solver", "image", "extension"):
        check(f"metadata: {key} is a non-empty string",
              isinstance(metadata.get(key), str) and metadata[key].strip(), repr(metadata.get(key)))
    check("metadata: extension starts with '.'", str(metadata.get("extension", "")).startswith("."),
          repr(metadata.get("extension")))
    check("metadata: enumeration is a Boolean", isinstance(metadata.get("enumeration"), bool),
          repr(metadata.get("enumeration")))
    if "optimization" in metadata:
        check("metadata: optimization is only ever false", metadata["optimization"] is False,
              "omit the key for an integration that optimises")
    if "compilation" in metadata:
        check("metadata: compilation is only ever true", metadata["compilation"] is True,
              "omit the key for an integration that does not compile")
    if "instance_binding" in metadata:
        check("metadata: instance_binding value", metadata["instance_binding"] in BINDINGS,
              f"one of {sorted(BINDINGS)}")

    others = {}
    for path in (root / "solvers").glob("*/metadata.yaml"):
        if path.parent.name != solver_id:
            try:
                others[path.parent.name] = json.loads(path.read_text(encoding="utf-8"))
            except ValueError:
                pass
    versions = {item.get("protocol_version") for item in others.values()}
    check("metadata: protocol_version matches the others",
          not versions or metadata.get("protocol_version") in versions,
          f"{metadata.get('protocol_version')!r}, others use {sorted(versions, key=str)}")
    clash = [other for other, item in others.items() if item.get("name") == metadata.get("name")]
    check("metadata: name is distinct", not clash, f"shared with {clash}")
    clash = [other for other, item in others.items() if item.get("image") == metadata.get("image")]
    check("metadata: image is distinct", not clash, f"shared with {clash}")

    paradigms = metadata.get("paradigms")
    known = {entry["id"] for entry in json.loads((root / "solvers/paradigms.json").read_text(encoding="utf-8"))}
    check("metadata: paradigms is a non-empty list without repeats",
          isinstance(paradigms, list) and paradigms and len(set(paradigms)) == len(paradigms), repr(paradigms))
    if isinstance(paradigms, list):
        unknown = [tag for tag in paradigms if tag not in known]
        check("metadata: paradigms are in solvers/paradigms.json", not unknown,
              f"add {unknown} to solvers/paradigms.json, or use one of {sorted(known)}")

    languages = literal_dict_keys(root / "generate_site.py", "LANGUAGES")
    extensions = literal_dict_keys(root / "generate_site.py", "EXTENSION_LANGUAGE")
    check("website: language has a LANGUAGES row", metadata.get("language") in languages,
          f"add {metadata.get('language')!r} to LANGUAGES in generate_site.py")
    check("website: extension is in EXTENSION_LANGUAGE", metadata.get("extension") in extensions,
          f"add {metadata.get('extension')!r} to EXTENSION_LANGUAGE in generate_site.py")


def check_dockerfile(solver_id, folder):
    text = (folder / "Dockerfile").read_text(encoding="utf-8")
    bases = re.findall(r"^\s*FROM\s+(\S+)", text, re.M | re.I)
    check("Dockerfile: has a FROM", bool(bases))
    unpinned = [base for base in bases if "@sha256:" not in base]
    check("Dockerfile: base images pinned by digest", not unpinned, f"unpinned {unpinned}")
    check("Dockerfile: copies its run.py", f"solvers/{solver_id}/run.py" in text,
          f"COPY solvers/{solver_id}/run.py into the image")
    check("Dockerfile: has an ENTRYPOINT", re.search(r"^\s*ENTRYPOINT\s", text, re.M | re.I) is not None)
    sources = []
    for line in re.findall(r"^\s*(?:COPY|ADD)\s+(.+)$", text, re.M | re.I):
        if "--from=" in line:  # a later build stage, not the build context
            continue
        parts = [part for part in line.split() if not part.startswith("--")]
        sources += parts[:-1]
    outside = [source for source in sources if not source.startswith(("runner", "solvers/"))]
    check("Dockerfile: copies only runner/ and solvers/", not outside,
          f"{outside} is outside the build context (.dockerignore)")
    loose = []
    for command in re.findall(r"pip3? install ([^\n&;\\]+)", text):
        loose += [arg for arg in command.split()
                  if not arg.startswith("-") and "==" not in arg and "@" not in arg and "/" not in arg]
    check("Dockerfile: pip packages pinned", not loose, f"unpinned {loose}", warn=True)


def check_scripts(root, folder, metadata):
    for name in ("run.py", "readiness_test.py"):
        try:
            compile((folder / name).read_text(encoding="utf-8"), name, "exec")
            report("PASS", f"{name}: compiles")
        except SyntaxError as error:
            report("FAIL", f"{name}: compiles", f"line {error.lineno}: {error.msg}")
    sys.path.insert(0, str(root))
    from generation.readiness import _required
    text = (folder / "readiness_test.py").read_text(encoding="utf-8")
    missing = sorted(name for name in _required(metadata) if f'"{name}"' not in text and f"'{name}'" not in text)
    check("readiness_test.py: names every required check", not missing, f"missing {missing}")


CONTRACT_HEADINGS = ("Submission file", "Entrypoint", "Instance", "Outputs", "Objective",
                     "Solving", "Compilation", "Environment", "Traps", "Example")


def check_contract(folder):
    """solvers/<id>/CONTRACT.md answers the mapping checklist of solvers/CONTRACT.md."""
    path = folder / "CONTRACT.md"
    if not check("contract: CONTRACT.md exists", path.is_file(),
                 f"write solvers/{folder.name}/CONTRACT.md (see solvers/CONTRACT.md, Mapping checklist)"):
        return
    headings = re.findall(r"^## (.+?)\s*$", path.read_text(encoding="utf-8"), re.M)
    missing = [heading for heading in CONTRACT_HEADINGS if heading not in headings]
    check("contract: has every checklist heading", not missing, f"missing {missing}")


def check_skill(root, folder):
    skills = sorted(path.parent for path in (folder / "skills").glob("*/SKILL.md"))
    if not check("skill: standalone skill exists", bool(skills), f"no {folder.name}/skills/<name>/SKILL.md"):
        return
    from generation.skills import rosetta_mentions, validate
    for skill in skills:
        try:
            validate(skill, project=True)
            report("PASS", f"skill {skill.name}: generation.skills validate --project")
        except (ValueError, OSError) as error:
            report("FAIL", f"skill {skill.name}: generation.skills validate --project", str(error))
        hits = rosetta_mentions(skill)
        check(f"skill {skill.name}: free of Rosetta text", not hits,
              "; ".join(hits[:5]) + (f" (+{len(hits) - 5} more)" if len(hits) > 5 else ""))


def check_certified(root, solver_id, metadata):
    pilots = literal_dict_keys(root / "tests/test_solvers.py", "PILOTS")
    check("tests: listed in PILOTS in tests/test_solvers.py", solver_id in pilots,
          "add it, with a fixture under tests/fixtures/")
    if metadata.get("optimization", True) is not False:
        swaps = literal_dict_keys(root / "tests/test_solvers.py", "MAXIMIZATION_SWAPS")
        check("tests: listed in MAXIMIZATION_SWAPS", solver_id in swaps,
              "add the minimise/maximise spelling its fixture uses")
    check("README.md names the integration", metadata.get("name", "") in
          (root / "README.md").read_text(encoding="utf-8"), f"add {metadata.get('name')!r} to README.md")


def check_readiness(root, solver_id):
    record = root / "solvers" / solver_id / "readiness.json"
    if not check("readiness: record exists", record.is_file(),
                 f"run python -m generation.readiness check --solver {solver_id} --output {record.relative_to(root)}"):
        return
    from generation.readiness import ReadinessError, verify
    try:
        verify(solver_id, record)
        report("PASS", "readiness: record matches current files and image")
    except (ReadinessError, Exception) as error:  # image lookup can fail with Docker errors too
        report("FAIL", "readiness: record matches current files and image", str(error))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("solver_id")
    parser.add_argument("--static", action="store_true", help="skip the readiness record (no Docker needed)")
    parser.add_argument("--repo", default=".", help="DCP-Bench Open repository root (default: current directory)")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    if not (root / "generation/readiness.py").is_file():
        sys.exit(f"{root} is not a DCP-Bench Open checkout; run from its root or pass --repo")
    folder = root / "solvers" / args.solver_id
    present = [check(f"files: {name}", (folder / name).is_file(), f"missing solvers/{args.solver_id}/{name}")
               for name in FILES]
    metadata = {}
    if present[0]:
        try:
            metadata = json.loads((folder / "metadata.yaml").read_text(encoding="utf-8"))
            check("metadata: JSON object", isinstance(metadata, dict), "the file must hold one JSON object")
        except ValueError as error:
            report("FAIL", "metadata: JSON object", f"metadata.yaml is parsed as JSON: {error}")
        if isinstance(metadata, dict) and metadata:
            check_metadata(root, args.solver_id, metadata)
        else:
            metadata = {}
    if present[1]:
        check_dockerfile(args.solver_id, folder)
    if all(present[2:]):
        check_scripts(root, folder, metadata)
    check_contract(folder)
    check_skill(root, folder)
    if not args.static:
        check_readiness(root, args.solver_id)
        if metadata and (folder / "readiness.json").is_file():
            check_certified(root, args.solver_id, metadata)
    failed, warned = results.count("FAIL"), results.count("WARN")
    print(f"\n{len(results) - failed - warned} passed, {warned} warnings, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
