"""Runs inside solver images only. Candidate imports never run on the host."""
import contextlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time


def strict_loads(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    def invalid(value):
        raise ValueError(f"Non-finite JSON value: {value}")
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)


def emit(record):
    print(json.dumps(record, allow_nan=False), flush=True)


def finish(status, detail="", **metadata):
    emit({"type": "status", "status": status, "detail": detail, **metadata})


def flatten(value):
    if isinstance(value, dict):
        return [x for v in value.values() for x in flatten(v)]
    if isinstance(value, (list, tuple)) or (hasattr(value, "ndim") and value.ndim > 0):
        return [x for v in value for x in flatten(v)]
    return [value]


def mapped(value, read):
    if isinstance(value, dict):
        return {k: mapped(v, read) for k, v in value.items()}
    if isinstance(value, (list, tuple)) or (hasattr(value, "ndim") and value.ndim > 0):
        return [mapped(v, read) for v in value]
    return read(value)


def build(request):
    spec = importlib.util.spec_from_file_location("candidate", "/input/model.py")
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        model, outputs = module.build(request["instance"])
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("build(instance) must return (model, nonempty output-expression dictionary)")
    return model, outputs


def python_solver(kind, request):
    start = time.monotonic()
    model, outputs = build(request)
    if kind == "cp_sat" and model.proto.has_floating_point_objective():
        return finish("unsupported", "Use an integer objective")
    flat = flatten(outputs)
    if kind == "cpmpy":
        from cpmpy.transformations.get_variables import get_variables
        # Register even output variables absent from the model's constraints.
        model += [variable >= variable.lb for variable in get_variables(flat)]
    count = 0
    solve_seconds = 0.0
    while count < request["solution_limit"]:
        left = request["execution_timeout"] - (time.monotonic() - start)
        if left <= 0:
            return finish("timeout", solve_seconds=solve_seconds)
        before = time.monotonic()
        if kind == "cpmpy":
            import cpmpy as cp
            from cpmpy.solvers.solver_interface import ExitStatus
            with contextlib.redirect_stdout(sys.stderr):
                ok = model.solve(solver="ortools", time_limit=left, num_search_workers=1)
            status = model.status().exitstatus
            optimal = not model.has_objective() or status == ExitStatus.OPTIMAL
            unsat = status == ExitStatus.UNSATISFIABLE
            def read(e):
                import numbers
                import numpy as np
                value = e.value() if hasattr(e, "value") else e
                if isinstance(value, (bool, np.bool_)):
                    return bool(value)
                if not isinstance(value, numbers.Integral):
                    raise ValueError("Declared outputs must be integer or Boolean values; no coercion from floats/strings")
                return int(value)
        else:
            from ortools.sat.python import cp_model
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = left
            solver.parameters.num_search_workers = 1
            status = solver.solve(model)
            ok = status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
            optimal = not model.has_objective() or status == cp_model.OPTIMAL
            unsat = status == cp_model.INFEASIBLE
            if status == cp_model.MODEL_INVALID:
                return finish("error", "Invalid CP-SAT model")
            read = lambda e: int(solver.value(e))
        solve_seconds += time.monotonic() - before
        if not ok:
            return finish("complete" if unsat and count else "unsat" if unsat else "timeout", solve_seconds=solve_seconds)
        if not optimal:
            return finish("timeout", "Candidate optimum was not proven", solve_seconds=solve_seconds)
        values = mapped(outputs, read)
        emit({"type": "solution", "values": values})
        count += 1
        if count == request["solution_limit"]:
            break
        if kind == "cpmpy":
            if model.has_objective():
                model = cp.Model(model.constraints + [model.objective_ == int(model.objective_value())])
            model += cp.any([e != read(e) for e in flat])
        else:
            if model.has_objective():
                if model.proto.has_floating_point_objective():
                    return finish("unsupported", "Use an integer objective")
                obj = model.proto.objective
                expression = sum(c * model.get_int_var_from_proto_index(i) for i, c in zip(obj.vars, obj.coeffs))
                value = solver.value(expression)
                model.clear_objective()
                model.add(expression == value)
            different = []
            for i, e in enumerate(flat):
                b = model.new_bool_var(f"_different_{count}_{i}")
                model.add(e != read(e)).only_enforce_if(b)
                different.append(b)
            model.add_bool_or(different)
    finish("limit", solve_seconds=solve_seconds)


def minizinc_solver(request):
    from datetime import timedelta
    import minizinc
    import re
    started = time.monotonic()
    source = Path("/input/model.mzn").read_text()
    # Integration convention: optimization uses a named integer `objective` and
    # an unannotated solve item on its own line. Never rewrite arbitrary syntax.
    solve_pattern = r"(?m)^\s*solve\s+(minimize|maximize)\s+objective\s*;\s*$"
    problem = minizinc.Model()
    problem.add_string(source)
    inst = minizinc.Instance(minizinc.Solver.lookup("gecode"), problem)
    if not request["legacy"]:
        for key, value in request["instance"].items():
            inst[key] = value
    optimization = inst.method != minizinc.Method.SATISFY
    seen = set()
    count = 0
    if optimization:
        result = inst.solve(time_limit=timedelta(seconds=request["execution_timeout"]), intermediate_solutions=False)
        if result.status == minizinc.Status.UNSATISFIABLE:
            return finish("unsat")
        if result.status != minizinc.Status.OPTIMAL_SOLUTION:
            return finish("timeout", "Candidate optimum was not proven")
        values = strict_loads(str(result.solution))
        emit({"type": "solution", "values": values})
        seen.add(json.dumps(values, sort_keys=True))
        count = 1
        if request["solution_limit"] == 1:
            return finish("limit")
        if len(re.findall(solve_pattern, source)) != 1:
            return finish("unsupported", "Enumeration requires `solve minimize objective;` or maximize on its own line")
        source = re.sub(solve_pattern, f"constraint objective = {int(result.objective)};\nsolve satisfy;", source)
        problem = minizinc.Model()
        problem.add_string(source)
        inst = minizinc.Instance(minizinc.Solver.lookup("gecode"), problem)
        for key, value in request["instance"].items():
            inst[key] = value
    # Stream all solutions, stopping once enough distinct declared outputs exist.
    import asyncio

    async def enumerate_solutions():
        nonlocal count
        left = request["execution_timeout"] - (time.monotonic() - started)
        if left <= 0:
            return finish("timeout")
        status = minizinc.Status.UNKNOWN
        stream = inst.solutions(all_solutions=True, time_limit=timedelta(seconds=left), intermediate_solutions=False)
        try:
            async for result in stream:
                status = result.status
                if result.solution is not None:
                    values = strict_loads(str(result.solution))
                    key = json.dumps(values, sort_keys=True)
                    if key in seen:
                        continue
                    seen.add(key)
                    emit({"type": "solution", "values": values})
                    count += 1
                    if count >= request["solution_limit"]:
                        return finish("limit")
        finally:
            await stream.aclose()
        exhausted = status in (minizinc.Status.ALL_SOLUTIONS, minizinc.Status.UNSATISFIABLE)
        finish("complete" if exhausted and count else "unsat" if exhausted else "timeout")

    asyncio.run(enumerate_solutions())


def cpp_solver(request):
    import shutil
    shutil.copyfile("/input/model.cpp", "/tmp/model.cpp")
    before = time.monotonic()
    for command in (["cmake", "-S", "/opt/cpp", "-B", "/tmp/build", "-DCMAKE_BUILD_TYPE=Release"],
                    ["cmake", "--build", "/tmp/build", "-j1"]):
        left = request["compilation_timeout"] - (time.monotonic() - before)
        if left <= 0:
            return finish("compilation_error", "Compilation timed out")
        try:
            result = subprocess.run(command, stdout=sys.stderr, stderr=sys.stderr, timeout=left)
        except subprocess.TimeoutExpired:
            return finish("compilation_error", "Compilation timed out")
        if result.returncode:
            return finish("compilation_error", "C++ compilation failed; see stderr")
    compile_seconds = time.monotonic() - before
    try:
        result = subprocess.run(["/tmp/build/candidate"], input=json.dumps(request), text=True,
                                timeout=request["execution_timeout"])
    except subprocess.TimeoutExpired:
        return finish("timeout", "C++ execution exceeded limit")
    if result.returncode:
        return finish("error", f"C++ process exited {result.returncode}")
    print(f"Compilation: {compile_seconds:.3f}s", file=sys.stderr)


def main(kind):
    try:
        request = json.loads(Path("/input/request.json").read_text())
        if kind != "cpp":
            import signal
            def timeout_handler(signum, frame):
                raise TimeoutError("Runner execution budget exceeded")
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.setitimer(signal.ITIMER_REAL, request["execution_timeout"])
        if request["legacy"] and kind in ("cpmpy", "cp_sat"):
            process = subprocess.run([sys.executable, "/input/model.py"], capture_output=True,
                                     text=True, timeout=request["execution_timeout"])
            print(process.stderr, file=sys.stderr)
            if process.returncode:
                return finish("error", f"Legacy process exited {process.returncode}")
            # Legacy compatibility: one JSON object, with optional whole log lines.
            objects = []
            for line in process.stdout.splitlines():
                try:
                    value = strict_loads(line)
                    if isinstance(value, dict):
                        objects.append(value)
                    else:
                        print(line, file=sys.stderr)
                except ValueError:
                    if line.lstrip().startswith("{"):
                        return finish("error", "Malformed JSON solution")
                    print(line, file=sys.stderr)
            if len(objects) != 1:
                return finish("error", "Expected exactly one JSON solution line")
            emit({"type": "solution", "values": objects[0]})
            return finish("limit")
        if kind == "minizinc":
            minizinc_solver(request)
        elif kind == "cpp":
            cpp_solver(request)
        else:
            python_solver(kind, request)
    except (subprocess.TimeoutExpired, TimeoutError):
        finish("timeout")
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))
