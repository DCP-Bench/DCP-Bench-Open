"""Validate, propose and regression-check versioned skill bundles.

Run only coordinator-chosen trusted regression commands. Candidate instructions
are never authority to choose their own acceptance tests.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid

import yaml

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def now():
    return datetime.now(timezone.utc).isoformat()


def inside(path, parent):
    path, parent = Path(path).resolve(), Path(parent).resolve()
    if not path.is_relative_to(parent) or path == parent:
        raise ValueError(f"Path must be inside {parent}: {path}")
    return path


def hashes(folder):
    folder = Path(folder).resolve()
    result = {}
    for file in sorted(folder.rglob("*")):
        if file.is_symlink():
            raise ValueError(f"Skill bundles cannot contain symlinks: {file}")
        if file.is_file():
            result[file.relative_to(folder).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
    return result


def validate(folder, project=False):
    folder = Path(folder).resolve()
    text = (folder / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not match:
        raise ValueError("Missing YAML frontmatter")
    metadata = yaml.safe_load(match[1])
    if not isinstance(metadata, dict):
        raise ValueError("Frontmatter must be a mapping")
    name, description = metadata.get("name"), metadata.get("description")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64 or name != folder.name:
        raise ValueError("Skill name must match its directory and use lowercase letters/digits/hyphens")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        raise ValueError("Invalid description")
    allowed = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
    if set(metadata) - allowed:
        raise ValueError("Unknown frontmatter fields")
    for field in ("license", "compatibility", "allowed-tools"):
        if field in metadata and (not isinstance(metadata[field], str) or not metadata[field].strip()):
            raise ValueError(f"Invalid {field}")
    if len(metadata.get("compatibility", "")) > 500:
        raise ValueError("Compatibility too long")
    extra = metadata.get("metadata", {})
    if not isinstance(extra, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in extra.items()):
        raise ValueError("Metadata must map strings to strings")
    files = hashes(folder)
    for file in folder.rglob("*.md"):
        for link in re.findall(r"\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
            if "://" in link or link.startswith("#"):
                continue
            target = inside(file.parent / link.split("#")[0], folder)
            if not target.is_file():
                raise ValueError(f"Broken resource link: {link}")
    if project:
        # Provenance is a plain sources.md: which documentation the instructions
        # came from. Bundle bytes are hashed per attempt, where it matters.
        if not (folder / "sources.md").is_file():
            raise ValueError("Project skill needs sources.md listing the documentation used")
        cases = read(folder / "evals/evals.json")
        if cases.get("schema_version") != 1 or cases.get("skill_name") != name or not cases.get("evals"):
            raise ValueError("Invalid project eval manifest")
        ids = set()
        for case in cases["evals"]:
            if (not isinstance(case, dict) or not isinstance(case.get("id"), str) or not case["id"]
                    or case["id"] in ids or not case.get("prompt") or not case.get("expected_output")
                    or not isinstance(case.get("prerequisites"), list) or not case.get("evidence_required")):
                raise ValueError("Invalid/duplicate behavioural case")
            ids.add(case["id"])
            assertions = case.get("assertions", [])
            if (not assertions or any(not isinstance(a, dict) or not a.get("id") or not a.get("requirement") for a in assertions)
                    or len({a["id"] for a in assertions}) != len(assertions)):
                raise ValueError("Invalid/duplicate behavioural assertions")
    return {"name": name, "files": files, "entrypoint_lines": len(text.splitlines()), "project_checked": project}


def propose(run, skill, candidate, evidence):
    run = inside(ROOT / "generation/runs" / run, ROOT / "generation/runs")
    if not (run / "run.json").is_file():
        raise ValueError("Initialize the run first")
    skill = inside(skill, ROOT)
    if not any(skill.is_relative_to(ROOT / part) for part in ("skills", "solvers")):
        raise ValueError("Canonical skill must live in skills/ or solvers/")
    candidate = Path(candidate).resolve()
    original = validate(skill, project=True)
    if validate(candidate, project=True)["name"] != original["name"]:
        raise ValueError("Proposed skill name changed")
    evidence = str(evidence).strip()
    if not evidence:
        raise ValueError("Provide the observed failure and evidence path")
    proposal = run / "skill-changes" / uuid.uuid4().hex
    proposal.mkdir(parents=True)
    shutil.copytree(skill, proposal / "before" / skill.name)
    shutil.copytree(candidate, proposal / "candidate" / skill.name)
    write(proposal / "proposal.json", {"schema_version": 1, "target": str(skill.relative_to(ROOT)),
          "name": skill.name, "base_hashes": hashes(skill), "candidate_hashes": hashes(candidate),
          "evidence": evidence, "created_at": now(), "status": "proposed"})
    log_change(proposal, "skill_proposed", {"target": str(skill), "evidence": evidence})
    return str(proposal)


def proposal_data(path):
    path = inside(path, ROOT / "generation/runs")
    return path, read(path / "proposal.json")


def log_change(path, kind, data):
    from .manage import _append_event
    run = next((p for p in Path(path).parents if (p / "run.json").is_file()), None)
    if run is None:
        raise ValueError("Skill change has no run")
    _append_event(run, kind, {"proposal": str(path), **data})


def check_proposal(path, checks_file):
    path, data = proposal_data(path)
    if data["status"] != "proposed":
        raise ValueError("Check each immutable proposal once; create a new proposal to retry")
    checks = read(checks_file)
    if not isinstance(checks, list) or not checks:
        raise ValueError("Checks must be a nonempty list of trusted argv/timeout objects")
    for check in checks:
        argv = check.get("argv")
        if not isinstance(argv, list) or not argv or any(not isinstance(x, str) for x in argv) or not any("{skill}" in x for x in argv):
            raise ValueError("Each check needs argv and a {skill} argument")
        if not 0 < check.get("timeout", 60) <= 600:
            raise ValueError("Check timeout must be 1..600 seconds")
    results = []
    for version, expected in (("before", data["base_hashes"]), ("candidate", data["candidate_hashes"])):
        bundle = path / version / data["name"]
        if hashes(bundle) != expected:
            raise ValueError("Proposal snapshot changed")
        validate(bundle, project=True)
        for check in checks:
            argv = [arg.replace("{skill}", str(bundle)) for arg in check["argv"]]
            try:
                result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=check.get("timeout", 60))
                record = {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
            except subprocess.TimeoutExpired:
                record = {"returncode": None, "stderr": "timeout", "stdout": ""}
            results.append({"version": version, "argv": argv, **record})
        if hashes(bundle) != expected:
            raise ValueError("Regression command changed its skill snapshot")
    passed = all(r["returncode"] == 0 for r in results if r["version"] == "candidate")
    write(path / "checks.json", {"checks": checks, "results": results, "passed": passed, "at": now()})
    data["status"] = "validated" if passed else "rejected"
    data["checks_hash"] = hashlib.sha256((path / "checks.json").read_bytes()).hexdigest()
    write(path / "proposal.json", data)
    log_change(path, "skill_checked", {"status": data["status"]})
    return {"status": data["status"], "results": results}


def apply(path):
    path, data = proposal_data(path)
    target = inside(ROOT / data["target"], ROOT)
    if not any(target.is_relative_to(ROOT / part) for part in ("skills", "solvers")):
        raise ValueError("Canonical target is outside skill locations")
    candidate = path / "candidate" / data["name"]
    if data["status"] != "validated" or not read(path / "checks.json")["passed"]:
        raise ValueError("Only validated proposals can be applied")
    if hashlib.sha256((path / "checks.json").read_bytes()).hexdigest() != data["checks_hash"]:
        raise ValueError("Validation evidence changed")
    if hashes(target) != data["base_hashes"] or hashes(candidate) != data["candidate_hashes"]:
        raise ValueError("Canonical skill or candidate changed; rebase into a new proposal")
    validate(candidate, project=True)
    # Both resolved locations stay under this checkout; retain the original for rollback.
    stage = inside(target.parent / (".skill-stage-" + uuid.uuid4().hex), ROOT)
    backup = inside(path / "previous-live-bundle", ROOT)
    shutil.copytree(candidate, stage)
    target.rename(backup)
    try:
        stage.rename(target)
    except OSError:
        backup.rename(target)
        raise
    data.update(status="applied", applied_at=now())
    write(path / "proposal.json", data)
    log_change(path, "skill_applied", {"target": str(target)})
    return {"status": "applied", "target": str(target), "backup": str(backup)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    sub = commands.add_parser("validate"); sub.add_argument("skill")
    sub.add_argument("--project", action="store_true", help="Also require sources.md and behavioural cases")
    sub = commands.add_parser("propose")
    for field in ("run", "skill", "candidate", "evidence"): sub.add_argument("--" + field, required=True)
    sub = commands.add_parser("check"); sub.add_argument("proposal"); sub.add_argument("--checks", required=True)
    sub = commands.add_parser("apply"); sub.add_argument("proposal")
    args = parser.parse_args()
    try:
        if args.command == "validate": result = validate(args.skill, args.project)
        elif args.command == "propose": result = propose(args.run, args.skill, args.candidate, args.evidence)
        elif args.command == "check": result = check_proposal(args.proposal, args.checks)
        else: result = apply(args.proposal)
        print(json.dumps(result, indent=2))
        return 1 if isinstance(result, dict) and result.get("status") == "rejected" else 0
    except (ValueError, OSError, KeyError, yaml.YAMLError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
