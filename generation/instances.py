"""Gate a candidate instance before it joins the dataset, and recheck retained models on it.

    python -m generation.instances status
    python -m generation.instances check PROBLEM candidates.json [--append]
    python -m generation.instances recheck PROBLEM --instances json:6 json:7 [--flag] [--jobs N]

`status` lists the problems that can take more instances, fewest first, and the
ones already judged not to, from the "Instances not added" section of SOURCES.md.

`check` applies the gates a script can decide. A candidate must have exactly the
example's fields (plus `name`, and a `note` saying where it comes from), the same
value types and nesting, no ragged or mixed rows the example does not already
have, and inputs that differ from every instance already listed. Then the
reference must find a solution, or prove the optimum, within 10 seconds on one
worker, three times over. `--append` adds the candidates that pass to the end of
the problem's JSON file, leaving the existing entries byte for byte as they were.

`recheck` runs every model retained for PROBLEM on the named instances through the
evaluator, under the limits that model was accepted with. A model the evaluator
rejects there is a model that fitted the instances it had seen; `--flag` records
it in `generation/flags.json`, which takes the pair out of the covered set in
`generation.next_work` and marks the model on the site. Timeouts, runs ended by
the memory limit and infrastructure failures are reported and never flagged.
"""
import argparse
import codecs
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from evaluation import evaluate
from evaluation.execution import ROOT
from evaluation.reference import ReferenceSession, available_instances, embedded_instance
from evaluation.results import EvaluationError

from .brief import describe, scalar_type
from .next_work import FLAGS, GENERATED

BAR_SECONDS = 10
RUNS = 3
TARGET = 5
SOURCES = ROOT / "SOURCES.md"
SKIPPED_HEADING = "## Instances not added"
NEXT_HEADING = "\n## "
METADATA_KEYS = ("name", "note")
# Reasons that say the model is wrong on this instance. Everything else a
# rejection can carry is a timeout, the memory limit, an infrastructure fault
# or a bad request, which say nothing about the model.
MODEL_FAILURES = ("invalid_solution", "suboptimal_solution", "no_solution", "execution_error",
                  "compilation_error", "invalid_output", "output_limit")


def dataset_files(problem):
    folder = ROOT / "dataset" / problem
    source = folder / f"{problem}.cpmpy.py"
    if not source.is_file():
        raise EvaluationError("invalid_request", f"No reference for {problem}")
    return source.read_text(encoding="utf-8-sig"), folder / f"{problem}.json"


def leaves(value, path=()):
    """Each scalar's container path and type: [[1, 2]] has ('list', 'list', 'int')."""
    if isinstance(value, list):
        for item in value:
            yield from leaves(item, path + ("list",))
    elif isinstance(value, dict):
        for item in value.values():
            yield from leaves(item, path + ("dict",))
    else:
        yield path + (scalar_type(value),)


def shape_failures(example, record):
    """Why a record cannot stand beside the example, field by field; empty when it can."""
    failures = []
    missing = sorted(set(example) - set(record))
    extra = sorted(set(record) - set(example) - set(METADATA_KEYS))
    if missing:
        failures.append(f"missing fields: {missing}")
    if extra:
        failures.append(f"fields the reference does not read: {extra}")
    for key in METADATA_KEYS:
        if key in record and (not isinstance(record[key], str) or not record[key].strip()):
            failures.append(f"{key} must be a nonempty string")
    if "note" not in record:
        failures.append("no note: say where the instance comes from and what it varies")
    for name in sorted(set(example) & set(record)):
        want, got = example[name], record[name]
        if isinstance(want, list) != isinstance(got, list) or isinstance(want, dict) != isinstance(got, dict):
            failures.append(f"{name}: {type(got).__name__} where the example has {type(want).__name__}")
            continue
        # An empty list has no leaves to compare, so it matches any element type.
        want_leaves, got_leaves = set(leaves(want)), set(leaves(got))
        if want_leaves and got_leaves and want_leaves != got_leaves:
            failures.append(f"{name}: elements {sorted(got_leaves)} where the example has {sorted(want_leaves)}")
        for kind in ("ragged", "mixed"):
            if describe(got)[kind] and not describe(want)[kind]:
                failures.append(f"{name}: {kind}, which the example is not")
    return failures


def reference_runs(source, record, runs=RUNS, bar=BAR_SECONDS):
    """Time the reference on a record `runs` times; the first failure ends it."""
    results = []
    for _ in range(runs):
        started = time.perf_counter()
        session = None
        try:
            session = ReferenceSession(source, record, bar)
            results.append({"seconds": round(time.perf_counter() - started, 2),
                            "is_optimization": session.metadata["is_optimization"],
                            "optimum": session.metadata["optimum"]})
        except EvaluationError as error:
            return results, f"{error.reason}: {error.detail}"
        finally:
            if session is not None:
                session.close()
    if len({item["optimum"] for item in results}) > 1:
        return results, "the proven optimum differs between runs"
    return results, None


def check(problem, candidates, runs=RUNS, bar=BAR_SECONDS):
    source, path = dataset_files(problem)
    existing = json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else []
    example = embedded_instance(source)
    if not example:
        raise EvaluationError("invalid_request", f"{problem} has no data fields, so it has one instance only")
    if not isinstance(candidates, list) or any(not isinstance(x, dict) for x in candidates):
        raise EvaluationError("invalid_request", "Candidates must be a JSON list of objects")
    passed, report = [], []
    for index, record in enumerate(candidates):
        item = {"index": index, "name": record.get("name"), "passed": False,
                "failures": shape_failures(example, record)}
        report.append(item)
        if item["failures"]:
            continue
        before = len(available_instances(source, existing + passed))
        if len(available_instances(source, existing + passed + [record])) == before:
            item["failures"].append("same inputs as an instance already listed or an earlier candidate")
            continue
        timed, failure = reference_runs(source, record, runs, bar)
        item["seconds"] = [run["seconds"] for run in timed]
        if failure:
            item["failures"].append(f"reference: {failure}")
            continue
        item.update(passed=True, is_optimization=timed[0]["is_optimization"], optimum=timed[0]["optimum"])
        passed.append(record)
    return {"problem": problem, "bar_seconds": bar, "runs": runs, "listed": len(existing),
            "passed": len(passed), "candidates": report}, passed


def skipped_problems(text=None):
    """Lines like "- `problem`: reason" under SOURCES.md's "Instances not added" heading."""
    if text is None:
        text = SOURCES.read_text(encoding="utf-8") if SOURCES.is_file() else ""
    section = text.split(SKIPPED_HEADING, 1)[1].split(NEXT_HEADING, 1)[0] if SKIPPED_HEADING in text else ""
    return dict(re.findall(r"^- `([A-Za-z0-9_-]+)`: *(.+)$", section, flags=re.M))


def status(target=TARGET):
    """Problems that can take more instances, fewest distinct instances first."""
    skipped, flagged = skipped_problems(), set()
    try:
        flagged = {item["model"] for item in json.loads(FLAGS.read_text(encoding="utf-8"))["flags"]}
    except (OSError, ValueError, KeyError, TypeError):
        pass
    open_problems, fixed = [], 0
    for folder in sorted(path.parent for path in (ROOT / "dataset").glob("*/*.cpmpy.py")):
        source, path = dataset_files(folder.name)
        if not embedded_instance(source):
            fixed += 1
            continue
        rows = json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else []
        count = len(available_instances(source, rows))
        if folder.name in skipped or count >= target:
            continue
        kept = [folder.relative_to(ROOT).as_posix() for folder, _, _ in retained_models(folder.name)]
        open_problems.append({"problem": folder.name, "instances": count, "retained_models": len(kept),
                              "flagged": sum(model in flagged for model in kept)})
    # Fewest instances first; among equals, the most retained models, since each
    # new instance there rechecks more of them.
    open_problems.sort(key=lambda item: (item["instances"], -item["retained_models"], item["problem"]))
    return {"target": target, "open": len(open_problems), "problems": open_problems,
            "skipped": skipped, "without_data_fields": fixed}


def format_record(record):
    """One field per line, a matrix one row per line: how the hand-written files read."""
    lines = []
    for key, value in record.items():
        text = json.dumps(value)
        if isinstance(value, list) and value and all(isinstance(row, list) for row in value):
            text = "[\n" + ",\n".join("      " + json.dumps(row) for row in value) + "\n    ]"
        lines.append(f"    {json.dumps(key)}: {text}")
    return "  {\n" + ",\n".join(lines) + "\n  }"


def append(path, records):
    """Add records after the last entry without reformatting the entries before them."""
    raw = path.read_bytes() if path.is_file() else b"[]"
    bom = raw.startswith(codecs.BOM_UTF8)
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    before = json.loads(text)
    head = text[:text.rstrip().rfind("]")].rstrip()
    blocks = ",\n".join(format_record(record) for record in records)
    joined = head + ("\n" if head.endswith("[") else ",\n") + blocks + "\n]\n"
    joined = joined.replace("\r\n", "\n").replace("\n", newline)
    if json.loads(joined) != before + records:
        raise EvaluationError("infrastructure_error", f"Appending to {path} would change its existing entries")
    path.write_bytes((codecs.BOM_UTF8 if bom else b"") + joined.encode("utf-8"))
    return [f"json:{len(before) + i}" for i in range(len(records))]


def retained_models(problem):
    """Every model retained for a problem on this evaluator's own acceptance."""
    for record_path in sorted((GENERATED / problem).glob("*/*/record.json")):
        try:
            record = json.loads(record_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if record.get("verdict_source") != "container_evaluator" or not record.get("evaluation", {}).get("accepted"):
            continue
        model = record_path.parent / (record.get("model_file") or "")
        if model.is_file():
            yield record_path.parent, record, model


def recheck_one(problem, folder, record, model, ids):
    """Evaluate one retained model on `ids` under the limits it was accepted with."""
    accepted_with = record["evaluation"]
    limits = dict(accepted_with["limits"])
    result = evaluate(model, problem, record["solver"], instance_ids=ids,
                      solution_limit=accepted_with["requested"]["solution_limit"],
                      # Records older than the option were evaluated without it.
                      tolerate_inconclusive=accepted_with["requested"].get("tolerate_inconclusive", False),
                      **limits)
    row = {"model": folder.relative_to(ROOT).as_posix(), "solver": record["solver"],
           "reason": result["reason"], "skipped": result.get("skipped_instances", []),
           "seconds": {item["id"]: round(item["execution_wall_seconds"], 2)
                       for item in result["instances"] if item.get("execution_wall_seconds") is not None}}
    failed = [item for item in result["instances"] if not item.get("accepted") and not item.get("skipped")]
    if result["accepted"]:
        row["outcome"] = "passed" if not row["skipped"] else "passed, some inconclusive"
    elif result["reason"] in MODEL_FAILURES and failed:
        row.update(outcome="failed", instance=failed[-1]["id"], detail=result.get("detail"))
        row["flag"] = {"problem": problem, "solver": record["solver"], "model": row["model"],
                       "instance": failed[-1]["id"], "instance_hash": failed[-1]["instance_hash"],
                       "reason": result["reason"], "detail": result.get("detail"),
                       "image": result.get("image"), "limits": result["limits"],
                       "evaluation": failed[-1], "recorded": time.strftime("%Y-%m-%d")}
    else:
        row.update(outcome="inconclusive", detail=result.get("detail"))
    return row


def recheck(problem, ids, jobs=1, progress=None):
    models = list(retained_models(problem))
    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        futures = [pool.submit(recheck_one, problem, folder, record, model, ids)
                   for folder, record, model in models]
        rows = []
        for future in futures:
            rows.append(future.result())
            if progress:
                progress(f'{rows[-1]["model"]}: {rows[-1]["outcome"]}')
    failed = sum(row["outcome"] == "failed" for row in rows)
    conclusive = sum(row["outcome"] != "inconclusive" for row in rows)
    return {"problem": problem, "instances": ids, "models": len(rows),
            "passed": sum(row["outcome"].startswith("passed") for row in rows),
            "failed": failed, "inconclusive": len(rows) - conclusive,
            # When most models disagree with the reference, the reference or the
            # instance is the likelier fault. The skill says what to do then.
            "most_failed": failed >= 2 and failed * 2 > conclusive,
            "rows": rows}


def record_flags(rows):
    """Add each failure to generation/flags.json once; return how many were new."""
    try:
        document = json.loads(FLAGS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        document = {"schema": 1, "comment": FLAGS_COMMENT, "flags": []}
    known = {(item.get("model"), item.get("instance_hash")) for item in document["flags"]}
    new = [row["flag"] for row in rows if "flag" in row
           and (row["flag"]["model"], row["flag"]["instance_hash"]) not in known]
    document["flags"].extend(new)
    FLAGS.write_text(json.dumps(document, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return len(new)


FLAGS_COMMENT = ("Retained models the evaluator rejected on an instance added after they were accepted. "
                 "Written by generation.instances recheck --flag. A flagged model stays in "
                 "generated_models/ and on the site, marked; generation.next_work no longer counts "
                 "its pair as covered, so a model that passes every instance can replace it.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status", help="problems that can take more instances")
    gate = commands.add_parser("check", help="gate candidate instances for one problem")
    gate.add_argument("problem")
    gate.add_argument("candidates", type=Path, help="JSON list of candidate records")
    gate.add_argument("--append", action="store_true", help="append the candidates that pass")
    again = commands.add_parser("recheck", help="run the retained models of one problem on some instances")
    again.add_argument("problem")
    again.add_argument("--instances", nargs="+", required=True)
    again.add_argument("--flag", action="store_true", help="record model failures in generation/flags.json")
    again.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            print(json.dumps(status(), indent=2))
            return 0
        if args.command == "check":
            report, passed = check(args.problem, json.loads(args.candidates.read_text(encoding="utf-8-sig")))
            if args.append and passed:
                report["appended"] = append(dataset_files(args.problem)[1], passed)
            print(json.dumps(report, indent=2))
            return 0 if report["passed"] == len(report["candidates"]) else 1
        report = recheck(args.problem, args.instances, args.jobs,
                         progress=lambda line: print(line, file=sys.stderr, flush=True))
        if args.flag:
            report["flags_added"] = record_flags(report["rows"])
        for row in report["rows"]:
            row.pop("flag", None)
        print(json.dumps(report, indent=2))
        return 0 if not report["failed"] else 1
    except (EvaluationError, OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
