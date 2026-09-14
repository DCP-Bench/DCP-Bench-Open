"""Narrow compatibility mapping; unknown framework names never imply Python."""
ALIASES = {"cpmpy": "cpmpy_python", "ortools": "ortools_cp_sat_python",
           "or-tools": "ortools_cp_sat_python", "minizinc": "minizinc_gecode"}


def solver_id(name):
    return ALIASES.get(name.lower(), name)


def metrics(result, problem, framework, submission, existing=None):
    metadata = dict(existing or {})
    item = result["instances"][0] if result["instances"] else {}
    optimization = item.get("is_optimization")
    accepted, reason = result["accepted"], result["reason"]
    badge = ("solution_valid_and_optimal" if optimization else "solution_valid") if accepted else (
        "solution_valid_not_optimal" if reason == "suboptimal_solution" else "solution_not_valid")
    metadata.update(schema=2, problem=problem, framework=framework, submission=submission,
                    verdict_source="container_evaluator",
                    origin_type=metadata.get("origin_type", "machine_generated"),
                    is_optimization=optimization, instances_checked=["example"] if result["instances"] else [],
                    evaluation=result,
                    verdict={"evaluation": "performed", "execution": "success" if "runner_status" in item else "failed",
                             "error": None if accepted else result.get("detail", reason),
                             "solution_extracted": item.get("solutions_checked", 0) > 0,
                             "solution": item.get("first_solution"),
                             "consistency": "passed" if accepted or reason == "suboptimal_solution" else "failed",
                             "objective": ("passed" if accepted else "failed") if optimization else "not_applicable",
                             "badge": badge})
    return metadata
