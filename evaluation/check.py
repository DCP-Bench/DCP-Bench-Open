"""Evaluate one unchanged submission against selected reference instances."""
import argparse
import json
import math
import importlib.metadata
from pathlib import Path
import sys
import time

from .execution import ROOT, execute, image_identity, integration, validate_records
from .reference import ReferenceSession, available_instances, choose_instances
from .results import EvaluationError, canonical, digest, strict_json


# Reasons that say "we could not tell", as opposed to "this model is wrong".
INCONCLUSIVE = ("reference_timeout", "execution_timeout", "memory_limit")


def evaluate(model_path, problem_id, solver_id, *, instance_count=1, instance_ids=None,
             solution_limit=1, execution_timeout=60, reference_timeout=60,
             compilation_timeout=120, memory_mb=2048, cpus=1, dataset_dir=None,
             legacy=False, reference_source=None, instances=None,
             tolerate_inconclusive=False):
    """Return a JSON-compatible result. Optional reference_source is trusted dataset code.

    With tolerate_inconclusive, an instance that only times out is recorded and
    skipped so the remaining instances are still checked, and acceptance needs at
    least one instance verified. A solution the reference rejects still fails the
    whole evaluation immediately: this relaxes coverage, never soundness.
    """
    started = time.perf_counter()
    result = {"accepted": False, "reason": "not_evaluated", "problem_id": problem_id, "solver_id": solver_id,
              "requested": {"instance_count": instance_count, "instance_ids": instance_ids,
                            "solution_limit": solution_limit,
                            "tolerate_inconclusive": tolerate_inconclusive},
              "limits": {"execution_timeout": execution_timeout, "reference_timeout": reference_timeout,
                         "compilation_timeout": compilation_timeout, "memory_mb": memory_mb, "cpus": cpus},
              "instances": [], "instances_checked": 0, "solutions_checked": 0,
              "unperformed_instances": [], "skipped_instances": []}
    result["evaluator_version"] = 1
    try:
        try:
            result["reference_runtime"] = {"python": sys.version.split()[0],
                                           **{name: importlib.metadata.version(name) for name in ("cpmpy", "ortools", "numpy")}}
        except importlib.metadata.PackageNotFoundError as error:
            raise EvaluationError("infrastructure_error", f"Missing reference dependency: {error}") from error
        for name, value in (("solution_limit", solution_limit), ("memory_mb", memory_mb)):
            if type(value) is not int or value < 1:
                raise EvaluationError("invalid_request", f"{name} must be a positive integer")
        for value in (execution_timeout, reference_timeout, compilation_timeout, cpus):
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise EvaluationError("invalid_request", "Time/CPU limits must be positive finite numbers")
        if instance_ids is not None and instance_count != 1:
            raise EvaluationError("invalid_request", "Choose instance_count or instance_ids")
        if not isinstance(problem_id, str) or not problem_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in problem_id):
            raise EvaluationError("invalid_request", "Invalid problem ID")
        model_path = Path(model_path).resolve()
        metadata = integration(solver_id)
        if model_path.suffix != metadata["extension"]:
            raise EvaluationError("invalid_request", f"Expected {metadata['extension']} entrypoint")
        model_bytes = model_path.read_bytes()
        result["model_hash"] = digest(model_bytes)
        if reference_source is None:
            base = Path(dataset_dir) if dataset_dir is not None else ROOT / "dataset"
            folder = base / problem_id
            try:
                reference_source = (folder / f"{problem_id}.cpmpy.py").read_text(encoding="utf-8-sig")
                instances = strict_json((folder / f"{problem_id}.json").read_text(encoding="utf-8-sig"))
            except (OSError, ValueError) as error:
                raise EvaluationError("reference_error", str(error)) from error
        result["reference_hash"] = digest(reference_source.encode())
        available = available_instances(reference_source, [] if instances is None else instances)
        result["instances_available"] = len(available)
        chosen = choose_instances(available, instance_count, instance_ids)
        result["unperformed_instances"] = [i for i, _ in chosen]
        if legacy and (len(chosen) != 1 or chosen[0][0] != "example" or solution_limit != 1):
            raise EvaluationError("unsupported_capability", "Legacy programs support only example/one solution")
        if solution_limit > 1 and not metadata["enumeration"]:
            raise EvaluationError("unsupported_capability", "This integration does not support enumeration")
        image = image_identity(metadata)
        result["image"] = {"tag": metadata["image"], "id": image}
        for instance_id, instance in chosen:
            result["unperformed_instances"].remove(instance_id)
            item = {"id": instance_id, "instance_hash": digest(instance), "accepted": False, "solutions_checked": 0}
            result["instances"].append(item)
            session = None
            try:
                reference_start = time.perf_counter()
                session = ReferenceSession(reference_source, instance, reference_timeout)
                item.update({k: v for k, v in session.metadata.items() if k != "ok"})
                item["reference_setup_seconds"] = time.perf_counter() - reference_start
                records, timing = execute(model_path, instance, metadata, image,
                                          solution_limit=solution_limit, execution_timeout=execution_timeout,
                                          compilation_timeout=compilation_timeout, memory_mb=memory_mb,
                                          cpus=cpus, legacy=legacy, model_bytes=model_bytes,
                                          outputs=session.metadata["outputs"])
                item.update(timing)
                solutions, status = validate_records(records)
                item["runner_status"] = status
                item["solutions_received"] = len(solutions)
                # A conforming runner never emits more than it was asked for. Without
                # this bound, duplicate records each cost a full reference solve, so
                # total checking time would not be bounded by any configured limit.
                if len(solutions) > solution_limit:
                    raise EvaluationError("invalid_output",
                                          f"Runner emitted {len(solutions)} solutions for a limit of {solution_limit}")
                # Solutions are checked before the runner's exit status is consulted.
                # A solution the reference rejects disproves the model whatever the
                # run did afterwards, so a late timeout or crash must not discard it.
                seen = set()
                checking = time.perf_counter()
                for solution in solutions:
                    normalized = session.check(solution)
                    if "first_solution" not in item:
                        item["first_solution"] = normalized
                    key = canonical(normalized)
                    if key in seen:
                        continue
                    seen.add(key)
                    item["solutions_checked"] += 1
                    result["solutions_checked"] += 1
                    if len(seen) == solution_limit:
                        break
                item["checking_seconds"] = time.perf_counter() - checking
                failure = {"timeout": "execution_timeout", "unsat": "no_solution", "error": "execution_error",
                           "unsupported": "unsupported_capability", "compilation_error": "compilation_error"}
                # A runner can outlive the solver process the kernel killed for
                # memory, and then reports whatever that looked like to it.
                if (status["status"] in failure or not solutions) and timing.get("oom_killed"):
                    raise EvaluationError("memory_limit", f"The kernel killed a process at the {memory_mb} MB memory "
                                                          f"limit; the runner reported {status['status']}: "
                                                          f"{status.get('detail', '')}")
                if status["status"] in failure:
                    raise EvaluationError(failure[status["status"]], status.get("detail", status["status"]))
                if not solutions:
                    raise EvaluationError("no_solution", "At least one solution is required")
                # Exhaustion is the runner's claim about the candidate model. A
                # conforming runner either reaches the requested count or reports it.
                if len(seen) < solution_limit and status["status"] != "complete":
                    raise EvaluationError("invalid_output",
                                          f"Runner returned {len(seen)} distinct solutions for a limit of "
                                          f"{solution_limit} without reporting exhaustion")
                item.update(accepted=True, reason="accepted")
                result["instances_checked"] += 1
            except EvaluationError as e:
                item.update(reason=e.reason, detail=e.detail)
                if tolerate_inconclusive and e.reason in INCONCLUSIVE:
                    item["skipped"] = True
                    result["skipped_instances"].append(instance_id)
                    continue
                raise
            finally:
                if session is not None:
                    session.close()
        if not result["instances_checked"]:
            raise EvaluationError("no_instance_verified",
                                  "Every selected instance was inconclusive; none was verified")
        result.update(accepted=True, reason="accepted")
    except EvaluationError as e:
        result.update(reason=e.reason, detail=e.detail)
    except SyntaxError as e:
        result.update(reason="reference_error", detail=str(e))
    except (OSError, ValueError, TypeError, KeyError) as e:
        result.update(reason="invalid_request", detail=str(e))
    finally:
        # argparse accepts nan/inf as floats; even invalid requests must yield JSON.
        result["limits"] = {key: str(value) if isinstance(value, float) and not math.isfinite(value) else value
                            for key, value in result["limits"].items()}
        result["total_wall_seconds"] = time.perf_counter() - started
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model_path", type=Path)
    parser.add_argument("--problem", required=True)
    parser.add_argument("--solver", required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--instance-count", type=int, default=1)
    group.add_argument("--instance-ids", nargs="+")
    parser.add_argument("--solution-limit", type=int, default=1)
    parser.add_argument("--execution-timeout", type=float, default=60)
    parser.add_argument("--reference-timeout", type=float, default=60)
    parser.add_argument("--compilation-timeout", type=float, default=120)
    parser.add_argument("--memory-mb", type=int, default=2048)
    parser.add_argument("--cpus", type=float, default=1)
    parser.add_argument("--legacy", action="store_true")
    args = vars(parser.parse_args())
    args["problem_id"] = args.pop("problem")
    args["solver_id"] = args.pop("solver")
    result = evaluate(**args)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    sys.exit(main())
