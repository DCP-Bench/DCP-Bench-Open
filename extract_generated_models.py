#!/usr/bin/env python3
"""Extract generated models from CP-Bench leaderboard submissions into generated_models/.

Downloads, for every submission under submissions/v1_verified in the HF repo
kostis-init/my-storage, the generated model code (submission.jsonl) and its
evaluation verdicts (results/v1_verified/<submission>/summary.txt), then writes
one folder per model:

    generated_models/<problem>/<framework>/<submission>/
        model.<ext>          # the code exactly as submitted
        metrics_passed.json  # provenance + parsed evaluation verdicts

Every model is imported (correct or not); the `verdict` records precisely what
the leaderboard evaluation found, and a derived `badge` is a suggestion only —
the front-end decides what to display.

Usage:
    python extract_generated_models.py

Requires only the Python standard library and network access to huggingface.co.
"""

import ast
import json
import re
import sys
import urllib.request
from pathlib import Path

HF_BASE = "https://huggingface.co"
DATASET_REPO = "kostis-init/my-storage"
VERSION = "v1_verified"
LEADERBOARD_URL = "https://huggingface.co/spaces/kostis-init/CP-Bench-Leaderboard-Live"
DATASET_JSONL = Path("dcp-bench-open.jsonl")
OUTPUT_DIR = Path("generated_models")

FRAMEWORK_EXTENSIONS = {"CPMpy": ".py", "OR-Tools": ".py", "MiniZinc": ".mzn"}
FRAMEWORK_DIRS = {"CPMpy": "cpmpy", "OR-Tools": "ortools", "MiniZinc": "minizinc"}

# Old CP-Bench id had a typo for this problem.
ID_ALIASES = {"csplib_006_golomb_rules": "csplib_006_golomb_rulers"}

# Regexes for the evaluation summary files (two known formats).
RE_MODEL_HEADER = re.compile(r"^--- Model: (\S+) ---$")
RE_EXEC_OK = re.compile(r"SUCCESS: Model executed successfully")
RE_EXEC_FAIL = re.compile(r"FAILED: Execution failed with error:\s*(.*)")
RE_SOLUTION_OK = re.compile(r"SUCCESS: Got solution:\s*(.*)")
RE_SOLUTION_NO_OUTPUT = re.compile(r"FAILED: No output from execution")
RE_SOLUTION_NO_JSON = re.compile(r"FAILED: Could not extract JSON solution from output:\s*(.*)")
RE_CONSISTENCY_OK = re.compile(r"CONSISTENCY: PASSED")
RE_CONSISTENCY_FAIL = re.compile(r"CONSISTENCY: FAILED.*")
RE_OBJECTIVE_OK = re.compile(r"OBJECTIVE CHECK: PASSED fully")
RE_OBJECTIVE_FAIL = re.compile(r"OBJECTIVE CHECK: FAILED.*")
RE_SKIPPED = re.compile(r"SKIPPED: Ground-truth model .* not found in dataset")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "opencode"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        return resp.read().decode("utf-8", errors="replace")


def list_submissions() -> list[str]:
    url = f"{HF_BASE}/api/datasets/{DATASET_REPO}/tree/main/submissions/{VERSION}"
    entries = json.loads(fetch(url))
    return sorted(e["path"].split("/")[-1] for e in entries if e["type"] == "directory")


def load_new_ids() -> set[str]:
    if not DATASET_JSONL.is_file():
        raise SystemExit(f"Missing {DATASET_JSONL}; run `python jsonl_convert.py` first.")
    with DATASET_JSONL.open(encoding="utf-8") as fh:
        return {json.loads(line)["id"] for line in fh if line.strip()}


def map_old_id(old_id: str, new_ids: set[str]) -> str | None:
    """Map an old CP-Bench id (e.g. aplai_course__1_bank_card) to the current id."""
    sub = old_id.split("__", 1)[-1]
    sub = ID_ALIASES.get(sub, sub)
    m = re.match(r"^(\d+)_(.+)$", sub)
    if m:
        candidate = f"session{m.group(1)}_{m.group(2)}"
        if candidate in new_ids:
            return candidate
    return sub if sub in new_ids else None


def parse_solution_payload(payload: str):
    try:
        return ast.literal_eval(payload)
    except Exception:
        return payload.strip()


def parse_summary(text: str) -> dict:
    """Parse an evaluation summary.txt into {old_id: verdict}."""
    verdicts = {}
    current = None
    for line in text.splitlines():
        m = RE_MODEL_HEADER.match(line.strip())
        if m:
            current = m.group(1)
            verdicts[current] = {
                "evaluation": "performed",
                "execution": "success",
                "error": None,
                "solution_extracted": None,
                "solution": None,
                "consistency": "unknown",
                "objective": "unknown",
            }
            continue
        if current is None:
            continue
        v = verdicts[current]
        if RE_SKIPPED.search(line):
            v["evaluation"] = "skipped"
            v["error"] = "ground-truth model not found in dataset, evaluation skipped"
        elif RE_EXEC_FAIL.search(line):
            v["execution"] = "failed"
            v["error"] = RE_EXEC_FAIL.search(line).group(1).strip()[:400] or "see summary"
        elif v["execution"] == "success" and RE_EXEC_OK.search(line):
            v["execution"] = "success"
        if m := RE_SOLUTION_OK.search(line):
            v["solution_extracted"] = True
            v["solution"] = parse_solution_payload(m.group(1))
        elif RE_SOLUTION_NO_OUTPUT.search(line):
            v["solution_extracted"] = False
            v["error"] = v["error"] or "no output from execution"
        elif m := RE_SOLUTION_NO_JSON.search(line):
            v["solution_extracted"] = False
            v["error"] = v["error"] or f"could not extract JSON solution: {m.group(1).strip()[:200]}"
        if RE_CONSISTENCY_OK.search(line):
            v["consistency"] = "passed"
        elif RE_CONSISTENCY_FAIL.search(line):
            v["consistency"] = "failed"
        if RE_OBJECTIVE_OK.search(line):
            v["objective"] = "passed"
        elif RE_OBJECTIVE_FAIL.search(line):
            v["objective"] = "failed"
    return verdicts


def derive_badge(v: dict) -> str:
    if v.get("evaluation") == "skipped":
        return "unknown"
    if v["execution"] == "failed" or v["solution_extracted"] is False:
        return "unknown"
    if v["consistency"] == "failed":
        return "solution_not_valid"
    if v["objective"] == "failed":
        return "solution_valid_not_optimal"
    if v["objective"] == "passed":
        return "solution_valid_and_optimal"
    return "solution_valid" if v["consistency"] == "passed" else "unknown"


def model_file_name(framework: str) -> str:
    ext = FRAMEWORK_EXTENSIONS.get(framework)
    if ext is None:
        raise SystemExit(f"Unknown modelling framework in metadata: {framework}")
    return f"model{ext}"


def write_model(new_id: str, framework: str, submission: str, code: str, verdict: dict,
                metadata: dict, old_id: str, result_url: str, new_ids: set[str]) -> str:
    fw_dir = FRAMEWORK_DIRS.get(framework, framework.lower())
    target_dir = OUTPUT_DIR / new_id / fw_dir / submission
    target_dir.mkdir(parents=True, exist_ok=True)

    model_path = target_dir / model_file_name(framework)
    model_path.write_text(code, encoding="utf-8")

    metrics = {
        "problem": new_id,
        "framework": framework,
        "submission": submission,
        "generated_by": {
            "base_llm": metadata.get("base_llm"),
            "dataset_version": metadata.get("dataset_version"),
        },
        "source": {
            "leaderboard": LEADERBOARD_URL,
            "submission_file": (
                f"{HF_BASE}/datasets/{DATASET_REPO}/blob/main/"
                f"submissions/{VERSION}/{submission}/submission.jsonl"
            ),
            "result_file": result_url,
            "original_id": old_id,
        },
        "verdict": {
            **verdict,
            "badge": derive_badge(verdict),
        },
        "instances_checked": [0],  # leaderboard evaluation used the first instance
    }
    metrics_path = target_dir / "metrics_passed.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return submission


def main() -> int:
    new_ids = load_new_ids()
    submissions = list_submissions()
    print(f"Found {len(submissions)} submissions under {VERSION}.")

    total_models = 0
    badge_counts = {}
    skipped = []
    for submission in submissions:
        try:
            metadata = json.loads(fetch(
                f"{HF_BASE}/datasets/{DATASET_REPO}/resolve/main/"
                f"submissions/{VERSION}/{submission}/metadata.json"
            ))
            submission_lines = fetch(
                f"{HF_BASE}/datasets/{DATASET_REPO}/resolve/main/"
                f"submissions/{VERSION}/{submission}/submission.jsonl"
            ).splitlines()
            summary_url = (
                f"{HF_BASE}/datasets/{DATASET_REPO}/blob/main/"
                f"results/{VERSION}/{submission}/summary.txt"
            )
            verdicts = parse_summary(fetch(
                f"{HF_BASE}/datasets/{DATASET_REPO}/resolve/main/"
                f"results/{VERSION}/{submission}/summary.txt"
            ))
        except Exception as e:
            skipped.append((submission, f"fetch/parse error: {e}"))
            continue

        framework = metadata.get("modelling_framework")
        if framework not in FRAMEWORK_EXTENSIONS:
            skipped.append((submission, f"unknown framework {framework!r}"))
            continue

        count = 0
        missing = 0
        unmapped_ids = set()
        for line in submission_lines:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            old_id = entry["id"]
            new_id = map_old_id(old_id, new_ids)
            if new_id is None:
                missing += 1
                unmapped_ids.add(old_id)
                continue
            verdict = verdicts.get(old_id) or {
                "evaluation": "performed",
                "execution": "unknown",
                "error": "no evaluation found in summary",
                "solution_extracted": None,
                "solution": None,
                "consistency": "unknown",
                "objective": "unknown",
            }
            write_model(new_id, framework, submission, entry["model"], verdict,
                        metadata, old_id, summary_url, new_ids)
            badge = derive_badge(verdict)
            badge_counts[badge] = badge_counts.get(badge, 0) + 1
            count += 1
        total_models += count
        print(f"  {submission:38s} framework={framework:9s} models={count:4d}"
              f" (unmapped ids: {missing})")
        for uid in sorted(unmapped_ids):
            print(f"      unmapped: {uid}")

    print(f"\nImported {total_models} models into {OUTPUT_DIR}.")
    print("Badge distribution (suggestion only):")
    for badge, n in sorted(badge_counts.items()):
        print(f"  {badge:34s} {n}")
    if skipped:
        print("Skipped submissions:")
        for name, reason in skipped:
            print(f"  {name}: {reason}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
