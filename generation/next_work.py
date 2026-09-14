"""Report what generation work remains: usable integrations and unmodelled pairs.

This is a work queue, not a progress metric: every problem in every framework
is the target, so the list grows when an integration is added. Its first job is
the gate — an integration appears as usable only when its readiness record
still verifies.

Eligibility uses this evaluator's own evidence only. A retained model counts
when `generated_models/PROBLEM/SOLVER/*/record.json` was produced by the
container evaluator and accepted. Models carrying a leaderboard or demo verdict
are reported but never treated as coverage: a different evaluator's verdict is
not this one's.
"""
import argparse
import json
import sys

from evaluation.execution import ROOT, integration
from evaluation.results import EvaluationError

from .readiness import ReadinessError, verify

GENERATED = ROOT / "generated_models"
BLOCKERS = ROOT / "generation" / "blockers.json"


def integrations():
    """Every declared integration, with whether it is usable right now."""
    result = []
    for path in sorted((ROOT / "solvers").glob("*/metadata.yaml")):
        solver_id = path.parent.name
        record = {"id": solver_id, "ready": False}
        readiness = path.parent / "readiness.json"
        try:
            metadata = integration(solver_id)
            record["enumeration"] = bool(metadata.get("enumeration"))
            if not readiness.is_file():
                raise ReadinessError("No readiness record: run the readiness checklist for this "
                                     "integration, then generation.readiness check")
            verify(solver_id, readiness)
            record["ready"] = True
        except (ReadinessError, EvaluationError, OSError) as error:
            record["blocker"] = str(error)
        result.append(record)
    return result


def _records():
    for path in GENERATED.glob("*/*/*/record.json"):
        try:
            yield path, json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue


def accepted_pairs():
    """(problem, solver) pairs this evaluator has accepted a model for."""
    return {(path.parents[2].name, path.parents[1].name) for path, record in _records()
            if record.get("verdict_source") == "container_evaluator"
            and record.get("evaluation", {}).get("accepted") is True}


def legacy_problems():
    """Problems whose only models carry another evaluator's verdict."""
    return {path.parents[2].name for path, record in _records()
            if record.get("verdict_source") != "container_evaluator"}


def blocked_pairs():
    """Pairs recorded as not worth attempting again, from generation/blockers.json.

    A null solver blocks the problem for every integration, which is right when
    the limit is in the reference rather than in any one solver.
    """
    try:
        record = json.loads(BLOCKERS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    entries = record.get("blockers") if isinstance(record, dict) else None
    return [item for item in entries or [] if isinstance(item, dict) and item.get("problem")]


def listed_instances(problem):
    """Upper bound on distinct instances: listed rows, or the embedded example alone.

    Exact identity needs the reference loader; this is enough to prefer problems
    where a hardcoded model can actually be caught.
    """
    path = ROOT / "dataset" / problem / f"{problem}.json"
    if not path.is_file():
        return 1
    try:
        rows = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return 1
    return max(1, len(rows)) if isinstance(rows, list) else 1


def report(limit=20, include_unready=False):
    problems = sorted(path.parent.name for path in (ROOT / "dataset").glob("*/*.cpmpy.py"))
    counts = {problem: listed_instances(problem) for problem in problems}
    declared = integrations()
    usable = [item["id"] for item in declared if item["ready"] or include_unready]
    accepted, legacy, blockers = accepted_pairs(), legacy_problems(), blocked_pairs()

    def blocked(problem, solver):
        return any(item["problem"] == problem and item.get("solver") in (None, solver)
                   for item in blockers)

    eligible = [{"problem": problem, "solver": solver, "instances": counts[problem]}
                for solver in usable for problem in problems
                if (problem, solver) not in accepted and not blocked(problem, solver)]
    withheld = [f'{item["problem"]} / {item.get("solver") or "every integration"}'
                for item in blockers]
    # Prefer pairs whose problem has several instances: there, a model that
    # hardcoded the example is caught by the evaluator instead of by review.
    eligible.sort(key=lambda item: (-item["instances"], item["problem"], item["solver"]))
    single = sum(1 for problem in problems if counts[problem] == 1)
    return {"problems": len(problems), "integrations": declared,
            "usable_integrations": usable, "accepted_pairs": len(accepted),
            "eligible_pairs": len(eligible), "next_pairs": eligible[:limit],
            "single_instance_problems": single,
            "blocked_pairs": withheld,
            "legacy_only_problems": len(legacy - {p for p, _ in accepted}),
            "note": "A model carrying another evaluator's verdict is not acceptance evidence. An integration "
                    "without a current readiness record cannot be used; set it up first. "
                    f"{single} of {len(problems)} problems have only the embedded example, "
                    "so for those the evaluator cannot detect a model that hardcoded it: "
                    "read such a model yourself before retaining it. Pairs in "
                    "generation/blockers.json are withheld from the queue; do not retry one "
                    "without new information, and add an entry when you block a pair."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=20, help="how many candidate pairs to list")
    parser.add_argument("--include-unready", action="store_true",
                        help="also list pairs for integrations that are not usable yet")
    args = parser.parse_args(argv)
    if args.limit < 0:
        print("generation.next_work: --limit must not be negative", file=sys.stderr)
        return 2
    print(json.dumps(report(args.limit, args.include_unready), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
