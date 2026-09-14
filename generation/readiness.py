"""Bind solver readiness evidence to the current integration and Docker image."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from evaluation.execution import ROOT as EVALUATION_ROOT, image_identity, integration
from evaluation.results import EvaluationError


ROOT = EVALUATION_ROOT
SCHEMA = 1
CHECK_SCRIPT = "readiness_test.py"
CHECK_TIMEOUT = 1800


class ReadinessError(ValueError):
    """A coordinator-correctable readiness evidence error."""


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReadinessError(f"Invalid JSON {path}: {error}") from error


def _write_new(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
    except FileExistsError as error:
        raise ReadinessError(f"Refusing to overwrite readiness record: {path}") from error


def _files(solver_id: str) -> tuple[dict[str, Any], dict[str, str]]:
    metadata = integration(solver_id)
    folder = ROOT / "solvers" / solver_id
    paths = {"metadata": folder / "metadata.yaml", "runner": folder / "run.py", "dockerfile": folder / "Dockerfile",
             "checks": folder / CHECK_SCRIPT}
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        raise ReadinessError(f"Integration is missing required files: {', '.join(missing)}")
    # Hashing the check script means editing it invalidates the record, so the
    # evidence always belongs to the checks that are actually in the tree.
    return metadata, {name: _hash(path) for name, path in paths.items()}


def _required(metadata: dict[str, Any]) -> set[str]:
    names = {"satisfaction", "changed_instances", "malformed_output", "empty_output",
             "timeout_cleanup", "isolation", "missing_image"}
    if metadata.get("optimization", True) is False:
        names.add("unsupported_optimization")
    else:
        names.update(("minimization", "maximization"))
    if metadata.get("enumeration") is True:
        names.add("enumeration")
    else:
        names.add("unsupported_enumeration")
    if metadata.get("compilation") is True:
        names.add("compilation_error")
    return names


def _relative(path: Path) -> str:
    """Evidence as a repository-relative POSIX path.

    A record is committed and has to verify on any checkout, so it may not
    carry the absolute path of the machine that produced it. Evidence outside
    the repository is refused rather than stored absolute: nobody else could
    reproduce it, so it is not evidence.
    """
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        raise ReadinessError(f"Readiness evidence must live inside the repository: {path}") from None
    return relative.as_posix()


def _resolve(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        raise ReadinessError(f"Readiness record evidence must be repository-relative: {value}")
    return (ROOT / path).resolve()


def _evidence(values: Any, base: Path) -> list[dict[str, str]]:
    if not isinstance(values, list) or not values:
        raise ReadinessError("Every readiness test needs non-empty evidence")
    result = []
    for value in values:
        if not isinstance(value, str) or not value:
            raise ReadinessError("Evidence paths must be non-empty strings")
        path = Path(value)
        if not path.is_absolute():
            path = base / path
        path = path.resolve()
        if not path.is_file():
            raise ReadinessError(f"Missing readiness evidence: {path}")
        result.append({"path": _relative(path), "sha256": _hash(path)})
    return result


def _tests(values: Any, metadata: dict[str, Any], base: Path) -> list[dict[str, Any]]:
    if not isinstance(values, list):
        raise ReadinessError("report.tests must be a list")
    result = []
    names = set()
    for item in values:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item["name"]:
            raise ReadinessError("Every readiness test needs a non-empty name")
        if item["name"] in names:
            raise ReadinessError(f"Duplicate readiness test: {item['name']}")
        names.add(item["name"])
        if item.get("passed") is not True:
            raise ReadinessError(f"Readiness test did not pass: {item['name']}")
        result.append({"name": item["name"], "passed": True, "evidence": _evidence(item.get("evidence"), base)})
    missing = sorted(_required(metadata) - names)
    if missing:
        raise ReadinessError(f"Missing required readiness tests: {', '.join(missing)}")
    return result


def run_checks(solver_id: str, output_dir: str | Path) -> Path:
    """Execute the integration's own check script and keep its output as evidence.

    The script must print a JSON object mapping check name to Boolean and exit
    zero only when every check passed. Running it here, rather than accepting a
    report someone typed, is what ties the record to an actual execution.
    """
    script = ROOT / "solvers" / solver_id / CHECK_SCRIPT
    if not script.is_file():
        raise ReadinessError(f"Integration has no {CHECK_SCRIPT}: write one before claiming readiness")
    directory = Path(output_dir).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    try:
        finished = subprocess.run([sys.executable, str(script)], cwd=ROOT, capture_output=True,
                                  text=True, timeout=CHECK_TIMEOUT)
    except subprocess.TimeoutExpired as error:
        raise ReadinessError(f"{CHECK_SCRIPT} exceeded {CHECK_TIMEOUT} seconds") from error
    (directory / "readiness-stderr.log").write_text(finished.stderr, encoding="utf-8")
    evidence = directory / "readiness-result.json"
    evidence.write_text(finished.stdout, encoding="utf-8")
    if finished.returncode != 0:
        raise ReadinessError(f"{CHECK_SCRIPT} exited {finished.returncode}; see {evidence} and its stderr log")
    results = _read(evidence)
    if not isinstance(results, dict) or not results:
        raise ReadinessError(f"{CHECK_SCRIPT} must print a JSON object of check name to Boolean")
    failed = sorted(name for name, value in results.items() if value is not True)
    if failed:
        raise ReadinessError(f"Readiness checks did not pass: {', '.join(failed)}")
    report = {"image_id": image_identity(integration(solver_id)),
              "tests": [{"name": name, "passed": True, "evidence": [str(evidence)]} for name in sorted(results)]}
    # The readiness record is the immutable artifact; this report and the raw
    # output are working evidence, so a rerun after a repair may replace them.
    report_file = directory / "readiness-report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, indent=2, sort_keys=True) + chr(10), encoding="utf-8")
    return report_file


def check(solver_id: str, report_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    report_file = Path(report_path).resolve()
    if not report_file.is_file():
        raise ReadinessError(f"Readiness report does not exist: {report_file}")
    report = _read(report_file)
    if not isinstance(report, dict):
        raise ReadinessError("Readiness report must be a JSON object")
    metadata, files = _files(solver_id)
    actual_image = image_identity(metadata)
    if report.get("image_id") != actual_image:
        raise ReadinessError("Report image_id does not match the current integration image")
    tests = _tests(report.get("tests"), metadata, report_file.parent)
    record = {"schema": SCHEMA, "accepted": True, "solver_id": solver_id, "metadata": metadata,
              "integration_files": files, "image_id": actual_image, "tests": tests,
              "report_sha256": _hash(report_file)}
    _write_new(Path(output_path).resolve(), record)
    return record


def _verify_tests(values: Any, metadata: dict[str, Any]) -> None:
    if not isinstance(values, list):
        raise ReadinessError("Readiness record tests must be a list")
    names = set()
    for item in values:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str) or item["name"] in names:
            raise ReadinessError("Readiness record has invalid/duplicate test names")
        names.add(item["name"])
        if item.get("passed") is not True or not isinstance(item.get("evidence"), list) or not item["evidence"]:
            raise ReadinessError(f"Readiness record has incomplete test: {item['name']}")
        for evidence in item["evidence"]:
            if not isinstance(evidence, dict) or not isinstance(evidence.get("path"), str) or not isinstance(evidence.get("sha256"), str):
                raise ReadinessError("Readiness record has invalid evidence")
            path = _resolve(evidence["path"])
            if not path.is_file() or _hash(path) != evidence["sha256"]:
                raise ReadinessError(f"Readiness evidence changed or disappeared: {path}")
    missing = sorted(_required(metadata) - names)
    if missing:
        raise ReadinessError(f"Readiness record lacks required tests: {', '.join(missing)}")


def verify(solver_id: str, record_path: str | Path) -> dict[str, Any]:
    record_file = Path(record_path).resolve()
    record = _read(record_file)
    if not isinstance(record, dict) or record.get("schema") != SCHEMA or record.get("accepted") is not True:
        raise ReadinessError("Invalid readiness record")
    if record.get("solver_id") != solver_id:
        raise ReadinessError("Readiness record solver ID does not match request")
    metadata, files = _files(solver_id)
    if record.get("metadata") != metadata or record.get("integration_files") != files:
        raise ReadinessError("Integration files or metadata changed since readiness check")
    if record.get("image_id") != image_identity(metadata):
        raise ReadinessError("Integration image changed since readiness check")
    _verify_tests(record.get("tests"), metadata)
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check_p = commands.add_parser("check", help="run the integration's checks and record the evidence")
    check_p.add_argument("--solver", required=True); check_p.add_argument("--output", required=True)
    check_p.add_argument("--evidence-dir", help="where to write the check output (default: beside --output)")
    check_p.add_argument("--report", help="use an existing report instead of running readiness_test.py")
    verify_p = commands.add_parser("verify", help="verify a readiness record remains current")
    verify_p.add_argument("--solver", required=True); verify_p.add_argument("--record", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "verify":
            result = verify(args.solver, args.record)
        else:
            report = args.report or run_checks(args.solver, args.evidence_dir or Path(args.output).resolve().parent)
            result = check(args.solver, report, args.output)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (ReadinessError, OSError, KeyError, TypeError, ValueError, EvaluationError) as error:
        print(f"generation.readiness: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
