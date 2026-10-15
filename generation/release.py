"""Release solver skills from development (solvers/) to the public skill repository (skills/).

A solver skill is developed in solvers/<id>/skills/<name>/ and released, when the user
decides it is ready, to skills/solvers/<name>/. Every release is recorded in
skills/versions.json: the version, a digest of what was published, the commit and git
tree it came from, and the evidence it was checked with. The README catalog, the
plugin marketplace and skills/CHANGELOG.md are kept in step. Nothing is committed: the
command prints a commit message for the user to use.
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
import tempfile

import yaml

from generation import skills

ROOT = skills.ROOT
PUBLISHED = "skills/solvers"
LEDGER = "skills/versions.json"
CHANGELOG = "skills/CHANGELOG.md"
CATALOG = "skills/README.md"
MARKETPLACE = "skills/.claude-plugin/marketplace.json"
FIRST_VERSION = "0.1.0"
SOLVERS_PLUGIN = "solvers"
SOLVERS_DESCRIPTION = ("Skills for individual constraint and optimisation solvers and modelling frameworks, "
                       "each teaching an agent to install one solver and model with its own API.")
CATALOG_START, CATALOG_END = "<!-- solver-skills:start -->", "<!-- solver-skills:end -->"
CHANGELOG_HEADER = ("# Changelog\n\nReleases of the solver skills under `solvers/`, newest first. "
                    "Written by `python -m generation.release`; the full record is `versions.json`.\n")


class ReleaseError(ValueError):
    """A release gate failed; nothing was written."""


def git(*args, check=True):
    done = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    if check and done.returncode:
        raise ReleaseError(f"git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout.strip() if done.returncode == 0 else None


def digest(folder):
    """SHA-256 over every file's relative path and content hash, sorted by path.

    Changes if and only if the folder's content changes. Computed the same way for the
    staged release and for the published copy, so `status` can detect direct edits.
    """
    lines = "".join(f"{path}\0{value}\n" for path, value in sorted(skills.hashes(folder).items()))
    return "sha256:" + hashlib.sha256(lines.encode()).hexdigest()


def parse_version(text):
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", text or "")
    if not match:
        raise ReleaseError(f"Version must look like X.Y.Z, got {text!r}")
    return tuple(int(part) for part in match.groups())


def next_version(current, bump=None, explicit=None):
    if explicit:
        if current and parse_version(explicit) <= parse_version(current):
            raise ReleaseError(f"--version {explicit} must be greater than the released {current}")
        parse_version(explicit)
        return explicit
    if not current:
        return FIRST_VERSION
    major, minor, patch = parse_version(current)
    return {"major": f"{major + 1}.0.0", "minor": f"{major}.{minor + 1}.0"}.get(
        bump or "patch", f"{major}.{minor}.{patch + 1}")


def stamp_version(skill_md, version):
    """Set metadata.version in the frontmatter, leaving every other line as it was."""
    text = skill_md.read_text(encoding="utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    match = re.match(r"\A---\r?\n(.*?\r?\n)---(\r?\n|$)", text, re.S)
    if not match:
        raise ReleaseError("SKILL.md has no frontmatter")
    lines = match[1].splitlines()
    line = f'  version: "{version}"'
    if any(re.match(r"metadata:\s*\S", item) for item in lines):
        raise ReleaseError("Write `metadata:` as a block mapping so the version can be stamped")
    if "metadata:" in [item.rstrip() for item in lines]:
        start = [item.rstrip() for item in lines].index("metadata:") + 1
        end = start
        while end < len(lines) and lines[end].startswith((" ", "\t")):
            end += 1
        block = [item for item in lines[start:end] if not re.match(r"\s+version:", item)]
        lines[start:end] = block + [line]
    else:
        lines += ["metadata:", line]
    front = newline.join(lines) + newline
    skill_md.write_text(text[:match.start(1)] + front + text[match.end(1):], encoding="utf-8")


def frontmatter(folder):
    text = (folder / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---", text, re.S)
    return yaml.safe_load(match[1]) if match else {}


def tested_with(folder):
    """The paragraph of sources.md that starts with 'Tested', as add-solver writes it."""
    path = folder / "sources.md"
    if not path.is_file():
        return None
    for paragraph in re.split(r"\n\s*\n", path.read_text(encoding="utf-8")):
        if paragraph.lstrip().startswith("Tested"):
            return " ".join(paragraph.split())
    return None


def read_ledger(root=None):
    path = (root or ROOT) / LEDGER
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"schema": 1, "skills": {}}


def released_skill(solver_id, root=None):
    """Repository-relative path of the released skill for an integration, or None."""
    for entry in read_ledger(root)["skills"].values():
        if entry.get("status") == "released" and entry.get("source", {}).get("solver_id") == solver_id:
            return entry["path"]
    return None


def skill_for(solver_id, root=None):
    """The solver skill to model with: the released copy, else the single development copy.

    Returns (path, released); path is None when there is no release and the integration
    has no development skill, or several to choose from.
    """
    root = root or ROOT
    released = released_skill(solver_id, root)
    if released and (root / released / "SKILL.md").is_file():
        return released, True
    found = sorted((root / "solvers" / solver_id / "skills").glob("*/SKILL.md"))
    return (found[0].parent.relative_to(root).as_posix() if len(found) == 1 else None), False


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def source_skill(solver_id, name=None):
    found = sorted(path.parent for path in (ROOT / "solvers" / solver_id / "skills").glob("*/SKILL.md"))
    if name:
        found = [path for path in found if path.name == name]
    if not found:
        raise ReleaseError(f"No skill {name or ''} under solvers/{solver_id}/skills/")
    if len(found) > 1:
        raise ReleaseError(f"Several skills in solvers/{solver_id}/skills/; pick one with --skill: "
                           + ", ".join(path.name for path in found))
    return found[0]


def stage(source, into):
    """Copy the git-tracked files of `source` into `into/<name>`; return the staged folder."""
    relative = source.relative_to(ROOT).as_posix()
    tracked = git("ls-files", "-z", "--", relative).split("\0")
    tracked = [item for item in tracked if item]
    if not tracked:
        raise ReleaseError(f"{relative} has no git-tracked files; add them before releasing")
    staged = into / source.name
    for item in tracked:
        target = staged / Path(item).relative_to(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        if (ROOT / item).is_file():  # a tracked file deleted in the working tree is not released
            shutil.copy2(ROOT / item, target)
    return staged


def gates(staged):
    try:
        skills.validate(staged, project=True)
    except (ValueError, OSError) as error:
        raise ReleaseError(f"generation.skills validate --project failed: {error}") from error
    hits = skills.rosetta_mentions(staged)
    if hits:
        raise ReleaseError("The skill mentions Rosetta/DCP-Bench; a released skill must stand alone:\n  "
                           + "\n  ".join(hits[:10]))


def readiness_evidence(solver_id):
    record = ROOT / "solvers" / solver_id / "readiness.json"
    if not record.is_file():
        return None
    data = json.loads(record.read_text(encoding="utf-8"))
    return {"record": record.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(record.read_bytes()).hexdigest(),
            "image_id": data.get("image_id")}


def regenerate_listings(ledger):
    """Rewrite the catalog table and marketplace entries from the ledger."""
    released = {name: entry for name, entry in sorted(ledger["skills"].items())
                if entry.get("status") == "released"}
    catalog = ROOT / CATALOG
    if catalog.is_file():
        rows = ["| Skill | Version | Path | Description |", "|---|---|---|---|"]
        rows += [f"| `{name}` | {entry['version']} | [solvers/{name}](solvers/{name}) | {entry['description']} |"
                 for name, entry in released.items()]
        block = "\n".join([CATALOG_START, *rows, CATALOG_END])
        text = catalog.read_text(encoding="utf-8")
        if CATALOG_START in text and CATALOG_END in text:
            text = re.sub(re.escape(CATALOG_START) + ".*?" + re.escape(CATALOG_END),
                          lambda _: block, text, flags=re.S)
        else:
            text = text.rstrip("\n") + ("\n\n## Solver skills\n\nReleased from `solvers/` with "
                                        "`python -m generation.release`; history in "
                                        "[versions.json](versions.json) and [CHANGELOG.md](CHANGELOG.md).\n\n"
                                        + block + "\n")
        catalog.write_text(text, encoding="utf-8")
    marketplace = ROOT / MARKETPLACE
    if not marketplace.is_file():
        print(f"warning: {MARKETPLACE} not found; marketplace not updated", file=sys.stderr)
        return
    data = json.loads(marketplace.read_text(encoding="utf-8"))
    # Every released solver skill sits in the one `solvers` plugin, which install tools show
    # as a group; other plugins (`meta`) are maintained by hand. The plugin has no
    # `version`, so Claude Code follows the repository's commits and every release reaches
    # its users; each skill's own version is stamped in its SKILL.md and the ledger.
    plugins = [item for item in data.get("plugins", [])
               if item.get("name") != SOLVERS_PLUGIN and not str(item.get("source", "")).startswith("./solvers/")]
    if released:
        plugins.append({"name": SOLVERS_PLUGIN,
                        "description": SOLVERS_DESCRIPTION + " Includes: " + ", ".join(released) + ".",
                        "source": "./solvers", "skills": [f"./{name}" for name in released]})
    data["plugins"] = plugins
    write_json(marketplace, data)


def add_changelog(entry):
    path = ROOT / CHANGELOG
    text = path.read_text(encoding="utf-8") if path.is_file() else CHANGELOG_HEADER
    head, _, rest = text.partition("\n## ")
    body = f"\n{entry.rstrip()}\n" + (f"\n## {rest}" if rest else "")
    path.write_text(head.rstrip("\n") + "\n" + body, encoding="utf-8")


def source_digest(solver_id, name=None):
    """Digest of the content a release of this skill would ship, before its version stamp.

    A standalone review names this digest, so it covers exactly what is released.
    """
    source = source_skill(solver_id, name)
    with tempfile.TemporaryDirectory(prefix="skill-digest-") as directory:
        return source.name, digest(stage(source, Path(directory)))


def checked_review(path, name, expected_digest):
    """The standalone review in `path`, if it is clean and covers exactly this content."""
    try:
        review = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ReleaseError(f"Cannot read the review {path}: {error}") from error
    if not isinstance(review, dict) or review.get("skill") != name:
        raise ReleaseError(f"The review {path} is not a review of {name}")
    if review.get("source_digest") != expected_digest:
        raise ReleaseError(f"The review covers {review.get('source_digest')}, but this release ships "
                           f"{expected_digest}: review the current content (python -m generation.release "
                           "digest <solver_id> gives the digest)")
    findings = review.get("findings")
    if review.get("verdict") != "standalone" or findings:
        listed = "\n  ".join(f"{item.get('file')}:{item.get('line')}: [{item.get('category')}] {item.get('why')}"
                             for item in (findings or []) if isinstance(item, dict))
        raise ReleaseError(f"The review found Rosetta content in {name}; fix it and review again:\n  " + listed)
    if not str(review.get("reviewer", "")).strip():
        raise ReleaseError(f"The review {path} does not say who reviewed")
    return {"verdict": "standalone", "reviewer": review["reviewer"],
            "file_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}


def publish(solver_id, message, name=None, bump=None, version=None, allow_dirty=False, dry_run=False,
            review=None, skip_review=False):
    source = source_skill(solver_id, name)
    name, relative = source.name, source.relative_to(ROOT).as_posix()
    dirty = bool(git("status", "--porcelain", "--untracked-files=all", "--", relative))
    if dirty and not allow_dirty:
        raise ReleaseError(f"{relative} has uncommitted changes; commit them, or pass --allow-dirty "
                           "(recorded as dirty in the ledger)")
    ledger = read_ledger()
    previous = ledger["skills"].get(name)
    current = previous["version"] if previous else None
    with tempfile.TemporaryDirectory(prefix="skill-release-") as directory:
        staged = stage(source, Path(directory))
        gates(staged)
        source_digest = digest(staged)
        if (previous and previous.get("status") == "released" and not bump and not version
                and previous.get("source_digest") == source_digest):
            print(f"{name} {current} is already released with this content; nothing to do "
                  "(pass --bump or --version to release it under a new version anyway)")
            return None
        if skip_review:
            reviewed = {"skipped": True}
            print(f"warning: releasing {name} without a standalone review (recorded in the ledger)", file=sys.stderr)
        elif review is None:
            raise ReleaseError("A release needs a clean standalone review: see "
                               "rosetta-skills/solver-setup/references/standalone-review.md, then pass "
                               "--review FILE (or --skip-review, which the ledger records)")
        else:
            reviewed = checked_review(review, name, source_digest)
        new = next_version(current, bump, version)
        stamp_version(staged / "SKILL.md", new)
        meta = frontmatter(staged)
        commit = git("rev-parse", "HEAD")
        entry = {
            "name": name, "status": "released", "version": new, "path": f"{PUBLISHED}/{name}",
            "description": " ".join(str(meta.get("description", "")).split()),
            "content_digest": digest(staged), "source_digest": source_digest,
            "released_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "released_by": git("config", "user.name", check=False) or "unknown",
            "message": message,
            "source": {"solver_id": solver_id, "path": relative, "commit": commit,
                       "tree": git("rev-parse", f"HEAD:{relative}", check=False), "dirty": dirty},
            "evidence": {"validate_project": "passed", "rosetta_free": True, "standalone_review": reviewed,
                         "readiness": readiness_evidence(solver_id), "tested_with": tested_with(staged)},
        }
        target = ROOT / PUBLISHED / name
        changed = [f"{PUBLISHED}/{name}/", LEDGER, CATALOG, MARKETPLACE, CHANGELOG]
        if dry_run:
            print(json.dumps(entry, indent=2))
            print(f"\nDry run: would write {', '.join(changed)}")
            return entry
        if target.exists():
            shutil.rmtree(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staged, target)
    history = []
    if previous:
        history = [{key: value for key, value in previous.items() if key != "history"},
                   *previous.get("history", [])]
    ledger["skills"][name] = {**entry, "history": history}
    write_json(ROOT / LEDGER, ledger)
    regenerate_listings(ledger)
    note = "" if not dirty else " (with uncommitted changes)"
    add_changelog(f"## {name} {new} — {entry['released_at'][:10]}\n\n{message.strip()}\n\n"
                  f"Source: `{relative}` at `{commit[:12]}`{note}.")
    if entry["evidence"]["readiness"] is None:
        print(f"warning: solvers/{solver_id}/readiness.json not found; released without integration evidence",
              file=sys.stderr)
    print("Wrote " + ", ".join(changed))
    print("\nSuggested commit message:\n")
    print(f"Release {name} {new}\n\n{message.strip()}\n\nSkill-Release: {name}@{new}\n"
          f"Skill-Source: {relative} @ {commit}{note}")
    return entry


def withdraw(name, message):
    ledger = read_ledger()
    entry = ledger["skills"].get(name)
    if not entry or entry.get("status") != "released":
        raise ReleaseError(f"{name} is not a released skill")
    target = ROOT / PUBLISHED / name
    if target.exists():
        shutil.rmtree(target)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    entry.update(status="withdrawn", withdrawn_at=now, withdrawn_because=message)
    write_json(ROOT / LEDGER, ledger)
    regenerate_listings(ledger)
    add_changelog(f"## {name} withdrawn — {now[:10]}\n\n{message.strip()}")
    print(f"Withdrew {name} {entry['version']}; wrote {PUBLISHED}/{name}/ (removed), {LEDGER}, "
          f"{CATALOG}, {MARKETPLACE}, {CHANGELOG}")


def status():
    """One row per solver skill and per published skill; returns the strict-mode problems."""
    ledger = read_ledger()["skills"]
    rows, problems = [], []
    sources = {path.parent.name: path.parent for path in sorted((ROOT / "solvers").glob("*/skills/*/SKILL.md"))}
    for name in sorted(set(sources) | set(ledger)):
        entry = ledger.get(name)
        notes = []
        if name in sources and (not entry or entry.get("status") != "released"):
            notes.append("unreleased" if not entry else "withdrawn")
        if entry and entry.get("status") == "released":
            published = ROOT / entry["path"]
            if not published.is_dir():
                notes.append("published copy missing")
                problems.append(name)
            elif digest(published) != entry["content_digest"]:
                notes.append("published copy edited directly")
                problems.append(name)
            if name in sources:
                with tempfile.TemporaryDirectory(prefix="skill-status-") as directory:
                    try:
                        same = digest(stage(sources[name], Path(directory))) == entry.get("source_digest")
                    except ReleaseError:
                        same = False
                notes.append("up to date" if same else "source changed since release")
            else:
                notes.append("source no longer in solvers/")
        version = entry["version"] if entry else "-"
        rows.append(f"{name:28} {version:9} {', '.join(notes)}")
    folder = ROOT / PUBLISHED
    for path in sorted(folder.iterdir()) if folder.is_dir() else []:
        if path.is_dir() and path.name not in ledger:
            rows.append(f"{path.name:28} {'-':9} published but not in {LEDGER}")
            problems.append(path.name)
    print("\n".join(rows) if rows else "No solver skills found.")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    publish_p = commands.add_parser("publish", help="release a solver skill to skills/solvers/")
    publish_p.add_argument("solver_id")
    publish_p.add_argument("--skill", help="skill folder name, when the integration has several")
    publish_p.add_argument("-m", "--message", required=True, help="what changed, for the changelog")
    choice = publish_p.add_mutually_exclusive_group()
    choice.add_argument("--bump", choices=("patch", "minor", "major"),
                        help="next version relative to the released one (default patch; first release is 0.1.0)")
    choice.add_argument("--version", help="explicit X.Y.Z, greater than the released version")
    publish_p.add_argument("--allow-dirty", action="store_true", help="release uncommitted changes (recorded)")
    publish_p.add_argument("--dry-run", action="store_true", help="run every gate, write nothing")
    reviewing = publish_p.add_mutually_exclusive_group()
    reviewing.add_argument("--review", metavar="FILE", help="the clean standalone review of this content")
    reviewing.add_argument("--skip-review", action="store_true", help="release without a review (recorded)")
    digest_p = commands.add_parser("digest", help="print the digest a standalone review must name")
    digest_p.add_argument("solver_id")
    digest_p.add_argument("--skill", help="skill folder name, when the integration has several")
    status_p = commands.add_parser("status", help="compare solvers/ skills with their releases")
    status_p.add_argument("--strict", action="store_true",
                          help="exit 1 if a published copy was edited directly, is missing, or is unrecorded")
    withdraw_p = commands.add_parser("withdraw", help="remove a released skill (the record is kept)")
    withdraw_p.add_argument("name")
    withdraw_p.add_argument("-m", "--message", required=True, help="why, for the changelog")
    args = parser.parse_args(argv)
    try:
        if args.command == "publish":
            publish(args.solver_id, args.message, args.skill, args.bump, args.version,
                    args.allow_dirty, args.dry_run, args.review, args.skip_review)
        elif args.command == "digest":
            name, value = source_digest(args.solver_id, args.skill)
            print(f"{name} {value}")
        elif args.command == "withdraw":
            withdraw(args.name, args.message)
        else:
            problems = status()
            if args.strict and problems:
                print(f"\nProblems: {', '.join(problems)}", file=sys.stderr)
                return 1
    except ReleaseError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
