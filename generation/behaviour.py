"""Prepare frozen skill trials and record evidence-backed independent assessments.

The host agent executes prompt.md; this module does not pretend a JSON manifest
is an LLM runtime. Assessment is explicit and preserves evidence hashes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

from .skills import hashes, read, validate, write


def prepare(skill, case_id, output):
    skill, output = Path(skill).resolve(), Path(output).resolve()
    validate(skill, project=True)
    manifest = read(skill / "evals/evals.json")
    cases = [case for case in manifest["evals"] if case["id"] == case_id]
    if len(cases) != 1 or manifest["skill_name"] != skill.name:
        raise ValueError("Unknown/duplicate case or mismatched skill")
    if output.is_relative_to(skill):
        raise ValueError("Trial output must be outside the skill")
    output.mkdir(parents=True, exist_ok=False)
    snapshot = output / "skill" / skill.name
    shutil.copytree(skill, snapshot)
    write(output / "trial.json", {"schema_version": 1, "case": cases[0], "skill": str(snapshot),
                                  "skill_hashes": hashes(snapshot), "state": "prepared"})
    (output / "prompt.md").write_text(cases[0]["prompt"] + "\n\nRead the frozen skill at " + str(snapshot / "SKILL.md") + "\n", encoding="utf-8")
    return str(output / "prompt.md")


def assess(trial, assessment):
    trial = Path(trial).resolve()
    if (trial / "result.json").exists():
        raise ValueError("Trial already assessed")
    data, report = read(trial / "trial.json"), read(assessment)
    if hashes(data["skill"]) != data["skill_hashes"]:
        raise ValueError("Frozen skill changed during trial")
    if not report.get("assessor") or not report.get("execution"):
        raise ValueError("Identify assessor and actual execution; prepared is not executed")
    # Assertions are the plain statements the manifest lists, keyed by their own
    # text, which is how the Agent Skills standard records a grading.
    expected = set(data["case"]["assertions"])
    observations = report.get("assertions", {})
    if set(observations) != expected:
        raise ValueError("Every assertion needs an explicit assessment")
    evidence = {}
    for key, item in observations.items():
        if type(item.get("passed")) is not bool or not item.get("observation") or not item.get("evidence"):
            raise ValueError(f"Assertion {key} requires Boolean result, observation and evidence files")
        for name in item["evidence"]:
            path = Path(name).resolve()
            if not path.is_file():
                raise ValueError(f"Missing evidence {path}")
            evidence[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    result = {"case_id": data["case"]["id"], "passed": all(a["passed"] for a in observations.values()),
              "assessment": report, "evidence_hashes": evidence, "skill_hashes": data["skill_hashes"]}
    write(trial / "result.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    for name in ("skill", "case", "output"): p.add_argument("--" + name, required=True)
    p = sub.add_parser("assess"); p.add_argument("trial"); p.add_argument("--assessment", required=True)
    args = parser.parse_args()
    try:
        result = prepare(args.skill, args.case, args.output) if args.command == "prepare" else assess(args.trial, args.assessment)
        print(json.dumps(result, indent=2))
        return int(isinstance(result, dict) and not result["passed"])
    except (OSError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
