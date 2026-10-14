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
declared-output assignment seen so far with a nogood. Auxiliary variables can repeat
an assignment of the declared outputs, so a round can add fewer new assignments than
it returned. A round that reports `d COMPLETE EXPLORATION` ends the enumeration.

Verification: ACE 2.6 accepts some invalid tuples (Product over four or more variables),
and re-solving with the outputs fixed does not catch them. Each solution is therefore
checked by the XCSP3 SolutionChecker from the same jar, on the round's own XML and the
full instantiation ACE printed for it. The checker evaluates each constraint itself, and
it also reports the objective cost, which must equal ACE's optimum. A rejected
assignment becomes a nogood and the search continues.

Errors: ACE and pycsp3 failures are reported as `error` with their message. ACE prints
the cause only with `-ev`, and pycsp3 prints its message before `SystemExit`.
"""
import importlib.util
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
from itertools import count
from pathlib import Path

sys.path.insert(0, "/opt/runner")
import runtime

MODEL = "/input/model.py"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
COMPLETE = re.compile(r"(?m)^\s*d COMPLETE EXPLORATION\s*$")
# ACE writes these when it stops on a failure (e.g. "Fatal Error: The id E is a keyword",
# "java.lang.OutOfMemoryError"). Without -ev it prints only "! ERROR", so -ev is passed.
FAILURE = re.compile(r"ERROR|Exception|OutOfMemoryError|Fatal Error")
ACE_OPTIONS = "-ev"
ACE_WRAPPER = "/opt/runner/ace"  # java -jar ACE-2.6.jar "$@" 2>&1, written by the Dockerfile
ACE_JAR = Path(importlib.util.find_spec("pycsp3").origin).parent / "solvers" / "ace" / "ACE-2.6.jar"
CHECKER = "org.xcsp.parser.callbacks.SolutionChecker"
INSTANTIATION = re.compile(r"<instantiation\b[^>]*>.*?</instantiation>", re.S)


class Timeout(Exception):
    pass


class Tee:
    """Passes writes through and keeps a copy, so pycsp3's printed error can be reported."""

    def __init__(self, stream):
        self.stream, self.kept = stream, []

    def write(self, text):
        self.kept.append(text)
        return self.stream.write(text)

    def flush(self):
        self.stream.flush()

    def text(self):
        return ANSI.sub("", "".join(self.kept))


def describe(error, printed):
    """The message of a failure. pycsp3 reports a modelling error as `ERROR: message`, then SystemExit."""
    if isinstance(error, SystemExit):
        lines = [line.split("ERROR:", 1)[1].strip() for line in printed.splitlines() if "ERROR:" in line]
        if lines:
            return "pycsp3: " + lines[-1]
    return f"{type(error).__name__}: {error}"


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
              "solutions": [], "instantiations": []}
    out, err = Tee(sys.stdout), Tee(sys.stderr)
    sys.stdout, sys.stderr = out, err
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
        result["detail"] = describe(error, out.text() + err.text())
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
    # pycsp3 leaves the JVM's stderr unread, so a Java exception such as OutOfMemoryError
    # never reaches the log. The image's wrapper merges stderr into stdout.
    from pycsp3.solvers.ace import ace as ace_module
    original_init = ace_module.Ace.__init__

    def wrapped_init(self):
        original_init(self)
        self.command = ACE_WRAPPER

    ace_module.Ace.__init__ = wrapped_init

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
                        options=f"-t={spec['time_limit']}s {ACE_OPTIONS}")
    log = pycsp3.solver().get_logger()
    text = ANSI.sub("", Path(log).read_text(encoding="utf-8", errors="replace")) if log and os.path.exists(log) else ""
    failures = [line.strip() for line in text.splitlines()
                if FAILURE.search(line) and "use -ev" not in line]
    if failures:
        result["status"] = "ERROR"
        result["detail"] = " | ".join(failures[:3])[:1000]
        return
    if status is None:
        raise RuntimeError("pycsp3 did not compile or solve the model")
    result["status"] = status.name
    result["complete"] = COMPLETE.search(text) is not None
    result["instantiations"] = INSTANTIATION.findall(text)
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
    result = json.loads(Path(spec["result"]).read_text(encoding="utf-8"))
    result["xml"] = str(outdir / "model-placeholder.xml")
    return result


class Found:
    """Checked solutions, and assignments the checker rejected. Both are excluded from later rounds."""

    def __init__(self, outputs, limit):
        self.outputs, self.limit = outputs, limit
        self.values, self.rejected, self.keys = [], [], set()

    @property
    def full(self):
        return len(self.values) >= self.limit

    @staticmethod
    def key(projected):
        return json.dumps(projected, sort_keys=True)

    def known(self, projected):
        return self.key(projected) in self.keys

    def remember(self, projected, valid):
        self.keys.add(self.key(projected))
        (self.values if valid else self.rejected).append(projected)

    def nogoods(self):
        return self.values + self.rejected


def verdict(xml, instantiation, bound, deadline):
    """True when the XCSP3 checker accepts the instantiation, and its cost is `bound` if both are known."""
    left = deadline - time.monotonic()
    if left < 3:
        raise Timeout()
    try:
        done = subprocess.run(["java", "-cp", str(ACE_JAR), CHECKER, xml, instantiation],
                              capture_output=True, text=True, timeout=left)
    except subprocess.TimeoutExpired as error:
        raise Timeout() from error
    text = done.stdout + done.stderr
    if "INVALID" in text:
        return False
    line = re.search(r"^OK(?:\t(-?\d+))?\s*$", text, re.M)
    if line is None:
        raise RuntimeError("the solution checker did not verify a solution: " + text.strip()[-300:])
    if bound is not None and line.group(1) is not None:
        return int(line.group(1)) == bound
    return True


def vet(found, result, indices, bound, deadline):
    """Verify the solutions at `indices`, in order. Returns how many new output assignments were seen."""
    new = 0
    if len(result["instantiations"]) != len(result["solutions"]):
        raise RuntimeError("ACE's solutions could not be paired with their instantiations")
    for index in indices:
        if found.full:
            break
        solution = result["solutions"][index]
        projected = {name: solution[name] for name in found.outputs}
        if found.known(projected):
            continue
        new += 1
        valid = verdict(result["xml"], result["instantiations"][index], bound, deadline)
        found.remember(projected, valid)
    return new


def decided(found):
    if found.values:
        return ("complete", "")
    if found.rejected:
        return ("error", "ACE reported only solutions that fail verification")
    return ("unsat", "")


def absorb(found, result, want, deadline):
    """(status, detail) when the enumeration is decided, else None."""
    if result["status"] == "UNSAT":
        return decided(found)
    new = vet(found, result, range(len(result["solutions"])), None, deadline)
    if found.full:
        return ("limit", "")
    if result["complete"]:
        return decided(found)
    if len(result["solutions"]) < want:
        return ("timeout", "The search stopped before it was exhausted")
    if new == 0:
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
    rounds = count(1)  # round 0 is the first solve; later rounds take the rest

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
            vet(found, first, range(len(first["solutions"]))[-1:], objective, deadline)
            if found.full:
                return flush("limit")
        else:
            objective = None
            decision = absorb(found, first, limit, deadline)
            if decision:
                return flush(*decision)
        while True:
            want = limit - len(found.values)
            result = run_round(job, next(rounds), deadline, sols=want, objective=objective,
                               nogoods=found.nogoods(), outputs=outputs)
            if result["status"] == "ERROR":
                return flush("error", result["detail"])
            decision = absorb(found, result, want, deadline)
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
