#!/usr/bin/env python3
"""Verify generated_models/<problem>/<framework>/cursor/model.py against CPMpy GT.

Writes metrics_passed.json next to each model. MiniZinc is unchanged in eval.py;
any other framework name is executed as Python that must print JSON.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from eval import (
    SCRIPT_EXECUTION_TIMEOUT,
    exec_code,
    extract_json_from_code_output,
    get_modified_script,
)

ROOT = Path(__file__).resolve().parent
GENERATED_DIR = ROOT / "generated_models"
DATASET_DIR = ROOT / "dataset"
SUBMISSION = "cursor"
BASE_LLM = "Cursor Grok 4.6"

# Display labels for site tabs. Unknown dirs fall back to the directory name.
FRAMEWORK_LABELS = {
    "choco": "Choco",
    "gcs": "GCS",
    "pumpkin": "Pumpkin",
    "scip": "SCIP",
    "highs": "HiGHS",
    "z3": "Z3",
    "cvc5": "cvc5",
    "exact": "Exact",
    "pysat": "PySAT",
    "pindakaas": "Pindakaas",
    "paramita": "Paramita",
    "hermax": "Hermax",
    "clingo": "Clingo",
    "clyngor": "Clyngor",
}


def framework_label(fw_dir: str, existing: dict | None) -> str:
    if existing and existing.get("framework"):
        return existing["framework"]
    return FRAMEWORK_LABELS.get(fw_dir, fw_dir)


def load_gt_script(problem_id: str) -> str:
    path = DATASET_DIR / problem_id / f"{problem_id}.cpmpy.py"
    if not path.is_file():
        raise FileNotFoundError(f"Ground-truth model not found: {path}")
    return path.read_text(encoding="utf-8")


def check_against_gt(gt_script: str, solution: dict) -> tuple[bool, bool, str, str]:
    modified = get_modified_script(gt_script, solution)
    tmp_dir = tempfile.mkdtemp(prefix="dcpbench_gt_")
    tmp_path = os.path.join(tmp_dir, "gt_check.py")
    try:
        with open(tmp_path, "w", encoding="utf-8") as tmp:
            tmp.write(modified)
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=SCRIPT_EXECUTION_TIMEOUT,
            encoding="utf-8",
        )
    finally:
        try:
            os.unlink(tmp_path)
            os.rmdir(tmp_dir)
        except OSError:
            pass

    stdout = result.stdout or ""
    stderr = result.stderr or ""
    consistency = "SUCCESS: Model is consistent" in stdout
    objective = (
        "SUCCESS: No objective defined" in stdout
        or "SUCCESS: Objective value is consistent" in stdout
    )
    return consistency, objective, stdout, stderr


def derive_badge(is_optimization: bool, consistency: bool, objective: bool) -> str:
    if not consistency:
        return "solution_not_valid"
    if not is_optimization:
        return "solution_valid"
    if objective:
        return "solution_valid_and_optimal"
    return "solution_valid_not_optimal"


def verify_model(model_path: Path) -> dict:
    cursor_dir = model_path.parent
    fw_dir = cursor_dir.parent.name
    problem_id = cursor_dir.parent.parent.name
    metrics_path = cursor_dir / "metrics_passed.json"
    existing = None
    if metrics_path.is_file():
        try:
            existing = json.loads(metrics_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = None

    framework = framework_label(fw_dir, existing)
    code = model_path.read_text(encoding="utf-8")
    ok, output, timed_out = exec_code(
        code, timeout=SCRIPT_EXECUTION_TIMEOUT, modelling_language=framework
    )

    metrics = {
        "problem": problem_id,
        "framework": framework,
        "submission": SUBMISSION,
        "generated_by": {"base_llm": BASE_LLM},
        "origin_type": "machine_generated",
        "is_optimization": False,
        "verdict": {
            "evaluation": "performed",
            "execution": "success" if ok else ("timeout" if timed_out else "failed"),
            "error": None if ok else (output or "execution failed"),
            "solution_extracted": False,
            "solution": None,
            "consistency": "unknown",
            "objective": "unknown",
            "badge": "unknown",
        },
        "instances_checked": [0],
    }

    if not ok:
        return metrics

    solution = extract_json_from_code_output(output)
    if solution is None:
        metrics["verdict"]["error"] = f"Could not extract JSON solution from output: {output}"
        return metrics

    metrics["verdict"]["solution_extracted"] = True
    metrics["verdict"]["solution"] = solution

    gt_script = load_gt_script(problem_id)
    consistency, objective, gt_stdout, gt_stderr = check_against_gt(gt_script, solution)
    metrics["verdict"]["consistency"] = "passed" if consistency else "failed"
    if not consistency:
        metrics["verdict"]["error"] = (
            f"CONSISTENCY FAILED, stdout: {gt_stdout}\nstderr: {gt_stderr}"
        )
        metrics["verdict"]["badge"] = derive_badge(False, False, False)
        return metrics

    if objective:
        metrics["verdict"]["objective"] = "not_applicable"
    else:
        metrics["verdict"]["objective"] = "failed"
    metrics["verdict"]["badge"] = derive_badge(False, True, objective)
    metrics["verdict"]["error"] = None
    return metrics


def iter_cursor_models(problem: str | None) -> list[Path]:
    root = GENERATED_DIR / problem if problem else GENERATED_DIR
    if not root.is_dir():
        return []
    return sorted(root.glob("*/cursor/model.py") if problem else root.glob("*/**/cursor/model.py"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problem", default="abbots_puzzle", help="Problem id to verify")
    parser.add_argument("--model", type=Path, help="Verify a single model.py instead of scanning")
    args = parser.parse_args()

    models = [args.model] if args.model else iter_cursor_models(args.problem)
    if not models:
        print("No cursor models found.", file=sys.stderr)
        return 1

    failed = 0
    for model_path in models:
        print(f"Verifying {model_path} ...", flush=True)
        metrics = verify_model(model_path)
        out_path = model_path.parent / "metrics_passed.json"
        out_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
        badge = metrics["verdict"]["badge"]
        err = metrics["verdict"].get("error")
        print(f"  {metrics['framework']}: {badge}" + (f" ({err})" if err else ""), flush=True)
        if badge not in {"solution_valid", "solution_valid_and_optimal"}:
            failed += 1

    print(f"Done. {len(models) - failed}/{len(models)} passed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
