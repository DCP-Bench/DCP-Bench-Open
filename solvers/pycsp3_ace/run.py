"""PyCSP3 2.6.1 modelling, compiled to XCSP3 and solved by the ACE-2.6 solver that
ships inside the pycsp3 wheel. Runs inside the pycsp3_ace image only.

Submission contract (one plain PyCSP3 script, model.py):

- `from pycsp3 import *` gives the instance as `data`, with every field of the
  instance JSON. A field is an attribute, `data.n`, or an item, `data["n"]`, which
  is the only form for a name such as `_SHIP`. Values are plain Python: lists of
  lists may be ragged, and nothing is converted to a named tuple. Metadata such as
  `name` or `note` is passed, and a model that never reads it is unaffected.
- Every declared output is a module-level name equal to the output name, bound to a
  `Var`, a `VarArray`, or a nested list of them. Integer and Boolean values are
  reported as integers 0/1.
- The model posts constraints with `satisfy(...)`, optionally one `minimize(...)`
  or `maximize(...)`, and never calls `solve()`. The runner calls solve.

The model is run in a child process per round, because pycsp3 keeps global state.
A round is one compile and one ACE run. The first round finds the solutions (up to
`solution_limit`). For an optimisation the first round uses ACE's full search, and
its last solution is reported only when ACE printed `s OPTIMUM`. Further rounds fix
the objective to its optimum (`satisfy(term == optimum)`), and exclude every
declared-output assignment found so far with a nogood. Auxiliary variables can repeat
an assignment of the declared outputs, so a round can add fewer new assignments than
it returned. A round that reports `d COMPLETE EXPLORATION` ends the enumeration.
"""
import json
import os
import re
import runpy
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, "/opt/runner")
import runtime

MODEL = "/input/model.py"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
COMPLETE = re.compile(r"(?m)^\s*d COMPLETE EXPLORATION\s*$")


class Timeout(Exception):
    pass


class Instance:
    """The instance as a model reads it: `data.field` or `data["field"]`."""

    def __init__(self, fields):
        self.__dict__.update(fields)

    def __getitem__(self, name):
        return self.__dict__[name]


# --- child: one pycsp3 compile and one ACE run in a fresh process -----------

def leaves(obj, variable):
    if isinstance(obj, list):
        return [x for item in obj for x in leaves(item, variable)]
    return [obj] if isinstance(obj, variable) else []


def differences(obj, value, variable):
    """Conditions that hold when an output differs from `value` (matrices element-wise)."""
    if isinstance(obj, list):
        return [c for o, v in zip(obj, value) for c in differences(o, v, variable)]
    return [obj != value] if isinstance(obj, variable) else []


def read(obj, k, variable):
    """The k-th recorded solution of a declared output, as plain integers."""
    if isinstance(obj, list):
        return [read(x, k, variable) for x in obj]
    if isinstance(obj, variable):
        value = obj.values[k]
        if not isinstance(value, int):
            raise ValueError("a declared output has no determined value in the solution")
        return int(value)
    if isinstance(obj, int):
        return int(obj)
    raise TypeError(f"declared output of type {type(obj).__name__} is not an integer variable")


def child(spec_path):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    result = {"status": "ERROR", "detail": "", "complete": False, "recorded": [], "bound": None,
              "solutions": []}
    try:
        # pycsp3 reads its options from argv when it is imported. The -data file is a
        # placeholder: pycsp3 would convert the real instance itself, and cannot take
        # field names with a leading underscore, so the instance is loaded below.
        sys.argv = [spec["model"], f"-data={spec['outdir']}/placeholder.json", f"-output={spec['outdir']}/"]
        Path(spec["outdir"], "placeholder.json").write_text('{"dcp_placeholder": 0}', encoding="utf-8")
        _child(spec, result)
    except BaseException as error:  # a modelling error may also end with SystemExit
        import traceback
        traceback.print_exc()
        result["status"] = "ERROR"
        result["detail"] = f"{type(error).__name__}: {error}"
    Path(spec["result"]).write_text(json.dumps(result, allow_nan=False), encoding="utf-8")
    sys.stdout.flush()
    sys.stderr.flush()
    # Skip atexit: pycsp3 would otherwise compile the model a second time.
    os._exit(0)


def _child(spec, result):
    import pycsp3
    from pycsp3.classes.main.variables import Variable
    from pycsp3.tools.utilities import ALL

    allowed = [False]
    real_solve = pycsp3.solve

    def guarded_solve(*args, **kwargs):
        if not allowed[0]:
            raise RuntimeError("the model must not call solve(); the runner solves it")
        return real_solve(*args, **kwargs)

    pycsp3.solve = guarded_solve
    fixed = spec["objective"]
    recorded = result["recorded"]

    def objective(original, direction):
        def post(term):
            recorded.append(direction)
            if fixed is not None:
                return pycsp3.satisfy(term == fixed)
            return original(term)
        return post

    pycsp3.minimize = objective(pycsp3.minimize, "min")
    pycsp3.maximize = objective(pycsp3.maximize, "max")

    # Replace pycsp3's own conversion (named tuples, which cannot hold names such as
    # `_SHIP`) before the model's `from pycsp3 import *` binds `data`.
    pycsp3.data = Instance(json.loads(Path(spec["instance"]).read_text(encoding="utf-8")))
    namespace = runpy.run_path(spec["model"], run_name="__main__")
    outputs = spec["outputs"]
    for name in outputs:
        if name not in namespace:
            raise NameError(f"the model does not define the declared output {name!r}")
    for nogood in spec["nogoods"]:
        literals = []
        for name, value in nogood.items():
            literals += differences(namespace[name], value, Variable)
        if not literals:  # every output is a constant equal to a found assignment
            result["status"] = "UNSAT"
            return
        pycsp3.satisfy(literals[0] if len(literals) == 1 else pycsp3.Or(*literals))

    optimising = bool(recorded) and fixed is None
    allowed[0] = True
    status = real_solve(solver=pycsp3.ACE, sols=ALL if optimising else spec["sols"],
                        options=f"-t={spec['time_limit']}s")
    if status is None:
        raise RuntimeError("pycsp3 did not compile or solve the model")
    result["status"] = status.name
    log = pycsp3.solver().get_logger()
    text = ANSI.sub("", Path(log).read_text(encoding="utf-8", errors="replace")) if log and os.path.exists(log) else ""
    result["complete"] = COMPLETE.search(text) is not None
    if recorded and fixed is None:
        result["bound"] = pycsp3.bound()
    if status.name in ("OPTIMUM", "SAT"):
        histories = []
        for name in outputs:
            for variable in leaves(namespace[name], Variable):
                if not variable.values:
                    # ACE reports only the variables that occur in a constraint.
                    raise ValueError(f"declared output {name!r} has a variable that no constraint "
                                     "mentions, so ACE does not report it; constrain it, e.g. satisfy(z >= 0)")
                histories.append(variable)
        count = len(histories[0].values) if histories else 0
        if any(len(v.values) != count for v in histories):
            raise ValueError("declared outputs have different numbers of recorded solutions")
        result["solutions"] = [{name: read(namespace[name], k, Variable) for name in outputs}
                               for k in range(count)]


# --- parent: rounds, projection, enumeration --------------------------------

def stop(process):
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    process.wait()


def run_round(job, index, deadline, *, sols, objective, nogoods, outputs):
    left = deadline - time.monotonic()
    if left < 3:
        raise Timeout()
    outdir = job / f"round{index}"
    outdir.mkdir()
    spec = {"model": MODEL, "instance": str(job / "instance.json"), "outdir": str(outdir),
            "sols": sols, "time_limit": int(left) - 2, "objective": objective,
            "nogoods": nogoods, "outputs": outputs, "result": str(outdir / "result.json")}
    (outdir / "spec.json").write_text(json.dumps(spec, allow_nan=False), encoding="utf-8")
    log_path = outdir / "child.log"
    with open(log_path, "w", encoding="utf-8") as log:
        process = subprocess.Popen([sys.executable, "/opt/runner/run.py", "--child", str(outdir / "spec.json")],
                                   stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                   start_new_session=True, cwd=str(outdir))
        try:
            process.wait(timeout=left)
        except subprocess.TimeoutExpired as error:
            raise Timeout() from error
        finally:
            stop(process)  # also ends any Java process the round started
    if not os.path.isfile(spec["result"]):
        tail = log_path.read_text(encoding="utf-8", errors="replace")[-2000:]
        raise RuntimeError(f"pycsp3 process exited {process.returncode} without a result: {tail}")
    return json.loads(Path(spec["result"]).read_text(encoding="utf-8"))


class Found:
    def __init__(self, outputs, limit):
        self.outputs, self.limit = outputs, limit
        self.values, self.seen = [], set()

    @property
    def full(self):
        return len(self.values) >= self.limit

    def take(self, solutions):
        added = 0
        for solution in solutions:
            if self.full:
                break
            projected = {name: solution[name] for name in self.outputs}
            key = json.dumps(projected, sort_keys=True)
            if key not in self.seen:
                self.seen.add(key)
                self.values.append(projected)
                added += 1
        return added


def absorb(found, result, want):
    """(status, detail) when the enumeration is decided, else None."""
    if result["status"] == "UNSAT":
        return ("complete", "") if found.values else ("unsat", "")
    added = found.take(result["solutions"])
    if found.full:
        return ("limit", "")
    if result["complete"]:
        return ("complete", "") if found.values else ("unsat", "")
    if len(result["solutions"]) < want:
        return ("timeout", "The search stopped before it was exhausted")
    if added == 0:
        return ("error", "A solution round returned no new output assignment")
    return None


def pycsp3_solver(request):
    deadline = time.monotonic() + request["execution_timeout"]
    limit = request["solution_limit"]
    outputs = list(request.get("outputs") or [])
    instance = request["instance"]
    if not outputs:
        return runtime.finish("error", "The request declares no outputs")
    found = Found(outputs, limit)
    job = Path(tempfile.mkdtemp(prefix="pycsp3_", dir="/tmp"))

    def flush(status, detail=""):
        for values in found.values[:limit]:
            runtime.emit({"type": "solution", "values": values})
        return runtime.finish(status, detail)

    try:
        (job / "instance.json").write_text(json.dumps(instance, allow_nan=False), encoding="utf-8")
        first = run_round(job, 0, deadline, sols=limit, objective=None, nogoods=[], outputs=outputs)
        if first["status"] == "ERROR":
            return runtime.finish("error", first["detail"])
        if first["recorded"]:
            if first["status"] == "UNSAT":
                return runtime.finish("unsat")
            if first["status"] != "OPTIMUM":
                return runtime.finish("timeout", "Candidate optimum was not proven")
            objective = first["bound"]
            if objective is None:
                return runtime.finish("error", "ACE proved an optimum without reporting its cost")
            found.take(first["solutions"][-1:])
            if found.full:
                return flush("limit")
        else:
            objective = None
            decision = absorb(found, first, limit)
            if decision:
                return flush(*decision)
        index = 1
        while True:
            want = limit - len(found.values)
            result = run_round(job, index, deadline, sols=want, objective=objective,
                               nogoods=found.values, outputs=outputs)
            index += 1
            if result["status"] == "ERROR":
                return flush("error", result["detail"])
            decision = absorb(found, result, want)
            if decision:
                return flush(*decision)
    except Timeout:
        return flush("timeout")
    except RuntimeError as error:
        return flush("error", str(error))
    finally:
        shutil.rmtree(job, ignore_errors=True)


runtime.python_solver = lambda kind, request: pycsp3_solver(request)

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--child":
        child(sys.argv[2])
    else:
        runtime.main("pycsp3")
