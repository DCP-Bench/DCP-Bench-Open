"""Create, evaluate, retain, and resume bounded model-generation attempts."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from evaluation import evaluate as evaluate_model
from evaluation.execution import integration
from evaluation.check import INCONCLUSIVE as INCONCLUSIVE_REASONS
from evaluation.results import EvaluationError


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = REPO_ROOT / "generation" / "runs"
GENERATED_ROOT = REPO_ROOT / "generated_models"
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")
PROFILE_DEFAULTS = {
    "instance_count": 1, "solution_limit": 1, "execution_timeout": 60,
    "reference_timeout": 60, "compilation_timeout": 120,
    "memory_mb": 2048, "cpus": 1, "tolerate_inconclusive": False,
}
PROFILE_KEYS = set(PROFILE_DEFAULTS) | {"instance_ids"}
RESERVED_EVENT_KINDS = {"run_initialized", "attempt_created", "attempt_evaluated",
                        "model_retained", "coordinator_failure", "setup_attempt_created"}


class ManagementError(ValueError):
    """A safe, user-correctable bookkeeping error."""


def _json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False)


def _write_new(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(_json(value) + "\n")
    except FileExistsError as error:
        raise ManagementError(f"Refusing to overwrite existing file: {path}") from error


def _read(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ManagementError(f"Invalid JSON file {path}: {error}") from error


def _identifier(value: str, label: str) -> str:
    if not IDENTIFIER.fullmatch(value):
        raise ManagementError(f"Invalid {label}: use 1-80 letters, digits, _ or -")
    return value


def _inside(path: Path, parent: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(parent.resolve())
    except ValueError as error:
        raise ManagementError(f"{label} must be inside {parent}") from error
    return resolved


def _run_dir(run_id: str) -> Path:
    return _inside(RUNS_ROOT / _identifier(run_id, "run ID"), RUNS_ROOT, "run directory")


def _run(run_id: str) -> tuple[Path, dict[str, Any]]:
    folder = _run_dir(run_id)
    record = folder / "run.json"
    if not record.is_file():
        raise ManagementError(f"Unknown run: {run_id}")
    data = _read(record)
    if data.get("id") != run_id or not isinstance(data.get("profile"), dict):
        raise ManagementError(f"Malformed run record: {record}")
    return folder, data


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _append_event(run_folder: Path, kind: str, data: dict[str, Any]) -> dict[str, Any]:
    _identifier(kind, "event kind")
    event = {"time": time.time(), "kind": kind, "data": data}
    with (run_folder / "events.jsonl").open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, sort_keys=True, allow_nan=False) + "\n")
    return event


def _load_config(config_path: str | None) -> dict[str, Any]:
    if config_path is None:
        return {}
    source = _inside(Path(config_path), REPO_ROOT, "configuration")
    if not source.is_file():
        raise ManagementError(f"Configuration does not exist: {source}")
    config = _read(source)
    if not isinstance(config, dict):
        raise ManagementError("Configuration must be a JSON object")
    return config


def init(run_id: str, config_path: str | None = None) -> Path:
    run_folder = _run_dir(run_id)
    if run_folder.exists():
        raise ManagementError(f"Run already exists: {run_id}")
    config = _load_config(config_path)
    agent = config.get("agent", "unknown")
    if not isinstance(agent, str) or not agent.strip():
        raise ManagementError("agent must be a non-empty string when provided")
    supplied_profile = config.get("profile", {})
    if not isinstance(supplied_profile, dict):
        raise ManagementError("profile must be a JSON object")
    unknown = set(supplied_profile) - PROFILE_KEYS
    if unknown:
        raise ManagementError(f"Unsupported profile keys: {sorted(unknown)}")
    profile = dict(PROFILE_DEFAULTS)
    profile.update(supplied_profile)
    if "instance_ids" in profile:
        if "instance_count" in supplied_profile:
            raise ManagementError("Choose instance_count or instance_ids, not both")
        ids = profile.pop("instance_ids")
        profile.pop("instance_count", None)
        if not isinstance(ids, list) or not ids or not all(isinstance(x, str) and x for x in ids):
            raise ManagementError("instance_ids must be a non-empty list of strings")
        profile["instance_ids"] = ids
    if not isinstance(profile["tolerate_inconclusive"], bool):
        raise ManagementError("tolerate_inconclusive must be true or false")
    # Let the evaluator validate numeric values too, but reject nonsensical stored profiles early.
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value <= 0
           for key, value in profile.items() if key not in ("instance_ids", "tolerate_inconclusive")):
        # Those two are checked above; all remaining profile values are limits.
        raise ManagementError("Profile limits must be positive finite numbers")
    integer_fields = [key for key in ("instance_count", "solution_limit", "memory_mb") if key in profile]
    if any(type(profile[key]) is not int for key in integer_fields):
        raise ManagementError("Instance, solution, and memory limits must be integers")
    run_folder.mkdir(parents=True)
    record = {"schema": 1, "id": run_id, "created_at": time.time(), "profile": profile, "agent": agent,
              "config": config, "config_hash": hashlib.sha256(_json(config).encode()).hexdigest()}
    _write_new(run_folder / "run.json", record)
    _append_event(run_folder, "run_initialized", {"profile": profile})
    return run_folder


def _skill_bundle(skill: str) -> tuple[Path, Path]:
    path = _inside(Path(skill), REPO_ROOT, "skill")
    root = path if path.is_dir() else path.parent
    if not (root / "SKILL.md").is_file():
        raise ManagementError("Skill must be a bundle directory or a SKILL.md within one")
    return path, root


def _skill_hash(bundle: Path) -> str:
    """One hash over every file in a skill bundle."""
    from .skills import hashes
    try:
        files = hashes(bundle)
    except (OSError, ValueError) as error:
        raise ManagementError(f"Unreadable skill bundle: {error}") from error
    if "SKILL.md" not in files:
        raise ManagementError("Skill bundle has no readable SKILL.md")
    return hashlib.sha256(_json(files).encode()).hexdigest()


def _skill_version(bundle: Path) -> dict[str, Any]:
    """Where the skill is, and which commit it was at.

    Git already versions the skill, so an attempt records its path and the
    commit it ran against instead of keeping a copy. `modified` says whether
    that path had uncommitted changes, because a commit alone would otherwise
    misrepresent a locally edited skill.
    """
    relative = bundle.relative_to(REPO_ROOT).as_posix()
    version: dict[str, Any] = {"path": relative, "commit": None, "modified": None}
    for key, command in (("commit", ["rev-parse", "HEAD"]),
                         ("modified", ["status", "--porcelain", "--", relative])):
        try:
            done = subprocess.run(["git", *command], cwd=REPO_ROOT, capture_output=True,
                                  text=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            continue
        if done.returncode == 0:
            version[key] = done.stdout.strip() if key == "commit" else bool(done.stdout.strip())
    return version


def _readiness(solver_id: str, record: Path | None = None) -> dict[str, Any]:
    from .readiness import verify
    path = record or REPO_ROOT / "solvers" / solver_id / "readiness.json"
    try:
        return verify(solver_id, path)
    except (OSError, ValueError, KeyError, EvaluationError) as error:
        raise ManagementError(f"Integration is not ready: {error}") from error


def attempt(run_id: str, problem_id: str, solver_id: str, skill: str) -> Path:
    run_folder, run = _run(run_id)
    _identifier(problem_id, "problem ID")
    _identifier(solver_id, "solver ID")
    readiness = _readiness(solver_id)
    supplied, bundle = _skill_bundle(skill)
    attempts = run_folder / "attempts" / problem_id / solver_id
    attempts.mkdir(parents=True, exist_ok=True)
    numbers = [int(x.name.split("-", 1)[1]) for x in attempts.iterdir()
               if x.is_dir() and re.fullmatch(r"attempt-\d{3}", x.name)]
    folder = attempts / f"attempt-{max(numbers, default=0) + 1:03d}"
    folder.mkdir()
    _write_new(folder / "readiness.json", readiness)
    record = {"schema": 2, "run_id": run_id, "problem_id": problem_id, "solver_id": solver_id,
              "attempt_id": folder.name, "created_at": time.time(),
              "skill_source": str(supplied.relative_to(REPO_ROOT)),
              "skill_version": _skill_version(bundle),
              "skill_bundle_hash": _skill_hash(bundle),
              "profile": run["profile"], "agent": run.get("agent", "unknown"),
              "readiness_hash": _sha256(folder / "readiness.json")}
    _write_new(folder / "attempt.json", record)
    _append_event(run_folder, "attempt_created", {"attempt": str(folder.relative_to(run_folder)),
                                                     "problem_id": problem_id, "solver_id": solver_id})
    return folder


def setup_attempt(run_id: str, solver_id: str, skill: str) -> Path:
    """Create a frozen, numbered setup-work directory for one integration."""
    run_folder, run = _run(run_id)
    _identifier(solver_id, "solver ID")
    supplied, bundle = _skill_bundle(skill)
    attempts = run_folder / "setup" / solver_id
    attempts.mkdir(parents=True, exist_ok=True)
    numbers = [int(item.name.split("-", 1)[1]) for item in attempts.iterdir()
               if item.is_dir() and re.fullmatch(r"setup-\d{3}", item.name)]
    folder = attempts / f"setup-{max(numbers, default=0) + 1:03d}"
    folder.mkdir()
    record = {"schema": 2, "run_id": run_id, "solver_id": solver_id, "setup_id": folder.name,
              "created_at": time.time(), "agent": run.get("agent", "unknown"),
              "profile": run["profile"], "skill_source": str(supplied.relative_to(REPO_ROOT)),
              "skill_version": _skill_version(bundle),
              "skill_bundle_hash": _skill_hash(bundle)}
    _write_new(folder / "setup.json", record)
    _append_event(run_folder, "setup_attempt_created", {"setup": str(folder.relative_to(run_folder)),
                                                           "solver_id": solver_id, "agent": record["agent"]})
    return folder


def _attempt(path: str | Path) -> tuple[Path, Path, dict[str, Any], dict[str, Any]]:
    folder = _inside(Path(path), RUNS_ROOT, "attempt")
    record = _read(folder / "attempt.json")
    run_folder, run = _run(record.get("run_id", ""))
    _inside(folder, run_folder, "attempt")
    if (not all(isinstance(record.get(key), str) for key in ("problem_id", "solver_id", "attempt_id", "skill_source"))
            or not isinstance(record.get("profile"), dict)
            or not isinstance(record.get("skill_bundle_hash"), str)):
        raise ManagementError("Malformed attempt record")
    for key, label in (("problem_id", "problem ID"), ("solver_id", "solver ID"), ("attempt_id", "attempt ID")):
        _identifier(record[key], label)
    expected_folder = run_folder / "attempts" / record["problem_id"] / record["solver_id"] / record["attempt_id"]
    if folder != expected_folder.resolve():
        raise ManagementError("Attempt record does not match its canonical path")
    # The skill is not copied, so the live bundle is what gets re-hashed. That
    # is the stronger check: editing the skill mid-attempt is what must not pass.
    _, bundle = _skill_bundle(str(REPO_ROOT / record["skill_source"]))
    if _skill_hash(bundle) != record["skill_bundle_hash"]:
        raise ManagementError("Skill bundle changed since the attempt was created")
    if record.get("readiness_hash") != _sha256(folder / "readiness.json"):
        raise ManagementError("Frozen readiness record changed")
    _readiness(record["solver_id"], folder / "readiness.json")
    return folder, run_folder, record, run


def _record_failure(folder: Path, failure: dict[str, Any]) -> None:
    failures = folder / "coordinator_failures"
    failures.mkdir(exist_ok=True)
    number = max((int(path.stem) for path in failures.glob("*.json") if path.stem.isdigit()), default=0) + 1
    _write_new(failures / f"{number:03d}.json", failure)


def evaluate(attempt_path: str, model_path: str) -> dict[str, Any]:
    folder, run_folder, record, run = _attempt(attempt_path)
    if (folder / "evaluation.json").exists():
        raise ManagementError("Attempt has already been evaluated")
    source = _inside(Path(model_path), REPO_ROOT, "model")
    if not source.is_file() or source.is_symlink():
        raise ManagementError("Model must be a regular file within the repository")
    existing_info = folder / "candidate.json"
    if existing_info.exists():
        candidate_info = _read(existing_info)
        candidates = [item for item in folder.glob("candidate.*") if item.name != "candidate.json"]
        if len(candidates) != 1 or _sha256(candidates[0]) != candidate_info.get("sha256"):
            raise ManagementError("Interrupted attempt has an altered candidate")
        if _sha256(source) != candidate_info["sha256"]:
            raise ManagementError("Retry model differs from preserved candidate")
        candidate, candidate_hash = candidates[0], candidate_info["sha256"]
    else:
        candidate = folder / f"candidate{source.suffix}"
        shutil.copy2(source, candidate)
        candidate_hash = _sha256(candidate)
        _write_new(existing_info, {"source": str(source.relative_to(REPO_ROOT)),
                                   "sha256": candidate_hash, "bytes": candidate.stat().st_size})
    profile = record["profile"]
    try:
        result = evaluate_model(candidate, record["problem_id"], record["solver_id"], **profile)
    except Exception as error:
        _record_failure(folder, {"time": time.time(), "error": repr(error), "candidate_sha256": candidate_hash})
        _append_event(run_folder, "coordinator_failure", {"attempt": str(folder.relative_to(run_folder)),
                                                            "error": repr(error)})
        return {"accepted": False, "reason": "coordinator_failure", "detail": repr(error)}
    if not isinstance(result, dict):
        _record_failure(folder, {"time": time.time(), "error": "Evaluator returned a non-object result"})
        raise ManagementError("Evaluator returned a non-object result")
    _write_new(folder / "evaluation.json", result)
    _append_event(run_folder, "attempt_evaluated", {"attempt": str(folder.relative_to(run_folder)),
                                                       "accepted": result.get("accepted", False),
                                                       "reason": result.get("reason")})
    return result


def retained_record(record: dict[str, Any], evaluation: dict[str, Any], model_file: str) -> dict[str, Any]:
    """The single record kept beside a retained model, in `record.json`.

    Every model under generated_models/ carries this shape, whether it came from
    the CP-Bench leaderboard or from this evaluator. `verdict_source` says which,
    because a leaderboard verdict was produced by different software on different
    infrastructure and must never read as though this evaluator had accepted it.
    """
    instances = evaluation.get("instances") or [{}]
    optimization = bool(instances[0].get("is_optimization"))
    checked, available = evaluation.get("instances_checked"), evaluation.get("instances_available")
    skipped = evaluation.get("skipped_instances") or []
    coverage = f"{checked} of {available} instances"
    if skipped:
        coverage += f", {len(skipped)} inconclusive and skipped"
    try:
        name = integration(record["solver_id"]).get("name", record["solver_id"])
    except EvaluationError:
        name = record["solver_id"]
    return {
        "schema": 2,
        "problem": record["problem_id"],
        "framework": name,
        "solver": record["solver_id"],
        "submission": f"{record['run_id']}-{record['attempt_id']}",
        "model_file": model_file,
        "verdict_source": "container_evaluator",
        "origin_type": "machine_generated",
        "is_optimization": optimization,
        "instances_checked": [item.get("id") for item in instances if item.get("accepted")],
        # What the acceptance is evidence of. A problem with one instance cannot
        # catch a model that fitted it, so say so here rather than leave a reader
        # to work it out from the instance list.
        "generality": {
            "instances_available": available,
            "evidenced_on": [item.get("id") for item in instances if item.get("accepted")],
            "skipped": [{"id": item.get("id"), "reason": item.get("reason")}
                        for item in instances if item.get("id") in skipped],
            "example_only": available == 1,
        },
        "generated_by": {"base_llm": record.get("agent", "unknown"),
                         "run": record["run_id"], "coverage": coverage},
        "source": {"note": f"Retained by the container evaluator: {coverage}, "
                           f"{evaluation.get('solutions_checked')} solutions checked."},
        "verdict": {"badge": "solution_valid_and_optimal" if optimization else "solution_valid",
                    "evaluation": "performed", "execution": "success",
                    "objective": "passed" if optimization else "not_applicable"},
        "evaluation": evaluation,
        "attempt": record,
    }


def retain(attempt_path: str) -> Path:
    folder, run_folder, record, run = _attempt(attempt_path)
    evaluation = _read(folder / "evaluation.json")
    candidate_info = _read(folder / "candidate.json")
    candidates = [candidate for candidate in folder.glob("candidate.*")
                  if candidate.name != "candidate.json"]
    if len(candidates) != 1:
        raise ManagementError("Expected exactly one preserved candidate file")
    candidate = candidates[0]
    actual_hash = _sha256(candidate)
    profile = record["profile"]
    expected_requested = {"instance_count": profile.get("instance_count", 1),
                          "instance_ids": profile.get("instance_ids"),
                          "solution_limit": profile["solution_limit"],
                          "tolerate_inconclusive": bool(profile.get("tolerate_inconclusive"))}
    expected_limits = {key: profile[key] for key in ("execution_timeout", "reference_timeout",
                                                       "compilation_timeout", "memory_mb", "cpus")}
    required = {"problem_id": record["problem_id"], "solver_id": record["solver_id"],
                "requested": expected_requested, "limits": expected_limits, "model_hash": actual_hash}
    for key, expected in required.items():
        if evaluation.get(key) != expected:
            raise ManagementError(f"Evaluation does not match immutable attempt {key}")
    if evaluation.get("accepted") is not True:
        raise ManagementError("Only a strictly accepted evaluator result can be retained")
    if evaluation.get("image", {}).get("id") != _read(folder / "readiness.json").get("image_id"):
        raise ManagementError("Evaluated image differs from the tested integration image")
    instances = evaluation.get("instances")
    supply = evaluation.get("instances_available")
    if type(supply) is not int or supply < 1:
        raise ManagementError("Evaluator result does not report available instance coverage")
    # A requested count is a budget: a problem with fewer distinct instances than
    # requested is fully covered by all of them. Named IDs are exact.
    coverage = len(profile.get("instance_ids", [])) or min(profile.get("instance_count", 1), supply)
    skipped = evaluation.get("skipped_instances")
    if (not isinstance(instances, list) or not instances or not isinstance(skipped, list)
            or evaluation.get("unperformed_instances") != [] or len(instances) != coverage
            or any(not isinstance(item, dict) for item in instances)):
        raise ManagementError("Evaluator result lacks complete accepted instance coverage")
    if profile.get("tolerate_inconclusive"):
        # Coverage may be partial, but every gap must be a recorded inconclusive
        # instance and at least one instance must actually have been verified.
        verified = [item for item in instances if item.get("skipped") is not True]
        if (not verified or evaluation.get("instances_checked") != len(verified)
                or len(instances) - len(verified) != len(skipped)
                or any(item.get("reason") not in INCONCLUSIVE_REASONS
                       for item in instances if item.get("skipped") is True)):
            raise ManagementError("Evaluator result has no verified instance or an unexplained skip")
    else:
        verified = instances
        if evaluation.get("instances_checked") != coverage:
            raise ManagementError("Evaluator result lacks complete accepted instance coverage")
    if any(item.get("accepted") is not True for item in verified):
        raise ManagementError("Evaluator result lacks complete accepted instance coverage")
    for item in verified:
        count = item.get("solutions_checked")
        if type(count) is not int or not 1 <= count <= profile["solution_limit"]:
            raise ManagementError("Evaluator result has invalid solution coverage")
        runner_status = item.get("runner_status")
        if count < profile["solution_limit"] and (not isinstance(runner_status, dict)
                                                    or runner_status.get("status") != "complete"):
            raise ManagementError("Incomplete solution coverage was not exhausted")
    # A skipped instance may have verified some solutions before timing out, so
    # the total covers every instance rather than only the accepted ones.
    if evaluation.get("solutions_checked") != sum(item.get("solutions_checked") or 0 for item in instances):
        raise ManagementError("Evaluator total solution coverage is inconsistent")
    if candidate_info.get("sha256") != actual_hash:
        raise ManagementError("Preserved candidate bytes changed after evaluation")
    destination = GENERATED_ROOT / record["problem_id"] / record["solver_id"] / f"{record['run_id']}-{record['attempt_id']}"
    _inside(destination, GENERATED_ROOT, "retention destination")
    if destination.exists():
        raise ManagementError(f"Refusing to overwrite retained model: {destination}")
    staging = destination.parent / f".{destination.name}.staging-{uuid.uuid4().hex}"
    staging.mkdir(parents=True)
    model_file = f"model{candidate.suffix}"
    shutil.copy2(candidate, staging / model_file)
    if _sha256(staging / model_file) != actual_hash:
        shutil.rmtree(staging, ignore_errors=True)
        raise ManagementError("Staged model hash verification failed")
    _write_new(staging / "record.json", retained_record(record, evaluation, model_file))
    try:
        os.rename(staging, destination)
    except OSError as error:
        shutil.rmtree(staging, ignore_errors=True)
        raise ManagementError(f"Could not atomically retain model: {error}") from error
    _write_new(folder / "retained.json", {"destination": str(destination.relative_to(REPO_ROOT)), "time": time.time()})
    _append_event(run_folder, "model_retained", {"attempt": str(folder.relative_to(run_folder)),
                                                   "destination": str(destination.relative_to(REPO_ROOT))})
    return destination


def event(run_id: str, kind: str, data_text: str) -> dict[str, Any]:
    folder, _ = _run(run_id)
    try:
        data = json.loads(data_text)
    except json.JSONDecodeError as error:
        raise ManagementError(f"--data must be a JSON object: {error}") from error
    if not isinstance(data, dict):
        raise ManagementError("--data must be a JSON object")
    if kind in RESERVED_EVENT_KINDS:
        raise ManagementError(f"{kind} is reserved for bookkeeping commands")
    return _append_event(folder, kind, data)


def status(run_id: str) -> dict[str, Any]:
    folder, run = _run(run_id)
    events = []
    events_file = folder / "events.jsonl"
    if events_file.exists():
        for line in events_file.read_text(encoding="utf-8").splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ManagementError(f"Malformed event log: {error}") from error
    outcomes = []
    for record in sorted(folder.glob("attempts/*/*/*/attempt.json")):
        attempt_record = _read(record)
        evaluation_file = record.parent / "evaluation.json"
        result = _read(evaluation_file) if evaluation_file.exists() else None
        outcomes.append({"attempt": str(record.parent.relative_to(folder)), "problem_id": attempt_record["problem_id"],
                         "solver_id": attempt_record["solver_id"], "evaluated": result is not None,
                         "accepted": result.get("accepted") if result else None,
                         "reason": result.get("reason") if result else None,
                         "retained": (record.parent / "retained.json").exists()})
    return {"run": run, "events": events, "outcomes": outcomes}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init_p = commands.add_parser("init", help="create a run")
    init_p.add_argument("--run", required=True); init_p.add_argument("--config")
    attempt_p = commands.add_parser("attempt", help="freeze a solver skill for one pair")
    attempt_p.add_argument("--run", required=True); attempt_p.add_argument("--problem", required=True)
    attempt_p.add_argument("--solver", required=True); attempt_p.add_argument("--skill", required=True)
    setup_p = commands.add_parser("setup-attempt", help="freeze a solver-setup skill")
    setup_p.add_argument("--run", required=True); setup_p.add_argument("--solver", required=True)
    setup_p.add_argument("--skill", required=True)
    eval_p = commands.add_parser("evaluate", help="evaluate a preserved candidate")
    eval_p.add_argument("--attempt", required=True); eval_p.add_argument("--model", required=True)
    retain_p = commands.add_parser("retain", help="persist an accepted immutable attempt")
    retain_p.add_argument("--attempt", required=True)
    event_p = commands.add_parser("event", help="append a non-acceptance event")
    event_p.add_argument("--run", required=True); event_p.add_argument("--kind", required=True); event_p.add_argument("--data", required=True)
    status_p = commands.add_parser("status", help="show resumable run outcomes")
    status_p.add_argument("--run", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "init": output = {"run": str(init(args.run, args.config))}
        elif args.command == "attempt": output = {"attempt": str(attempt(args.run, args.problem, args.solver, args.skill))}
        elif args.command == "setup-attempt": output = {"setup": str(setup_attempt(args.run, args.solver, args.skill))}
        elif args.command == "evaluate":
            output = evaluate(args.attempt, args.model)
            print(_json(output))
            return 0 if output.get("accepted") is True else 1
        elif args.command == "retain": output = {"retained": str(retain(args.attempt))}
        elif args.command == "event": output = event(args.run, args.kind, args.data)
        else: output = status(args.run)
        print(_json(output))
        return 0
    except ManagementError as error:
        print(f"generation.manage: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
