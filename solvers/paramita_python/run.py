"""Runner protocol for the Paramita (Python) integration. Runs inside the image only.

A submission is written against `paramita.modelling` and defines
`build(instance)`, which returns one of:

- `(subject_to, outputs)` for a satisfaction problem;
- `(subject_to, outputs, objective)` for an optimisation problem, where
  `objective` is `("minimize", expr)` or `("maximize", expr)`.

`subject_to` is a Boolean expression, or a list of them, built from `Bool`
variables with And, Or, Not, If, Iff, and PB comparisons over weighted sums of
Bools such as `2 * a + 3 * b + c <= 4`. `Xor` (and `^`) is not supported by
`to_cnf`: expand it into And, Or and Not. An expression is a linear integer
expression over Bools, `sum(w * b) + c`, and it is what an objective and an
integer output are built from.

`outputs` maps each declared name to one of: a Bool or any Boolean expression
over Bools, which the runner reads as a JSON boolean; an integer expression over
Bools, which it reads as a JSON integer; an int constant; or nested lists and
dicts of these. The value of each output is read from the solver's assignment.

The runner encodes every constraint with `to_cnf`, using the default PB encoder,
through one `DimacsVariablePool` per encoding:

- satisfaction: `add_to_container` into `SatSolver.from_name("Cadical300")`;
- optimisation: `add_to_weighted_container` into
  `MaxSatSolver.from_name("EvalMaxSAT2022")`. That call maximises its objective
  argument, so `maximize` passes the expression and `minimize` passes its
  negation. The constant it returns and `benefit()` together give the objective
  value, which the runner checks against the expression before it trusts the
  direction.

Integers are 32-bit in paramita. A coefficient outside that range is a Python
TypeError, and an expression whose value leaves it wraps around without an
error. The evaluator then rejects the wrong value, so the runner does not check
for wrapping itself.

Satisfaction enumerates up to the solution limit, blocking the declared outputs
rather than the whole assignment, so two models that agree on every output
count once. Enumeration stops early only when the solver proves no other
solution exists.

Optimisation reports only a proven optimum. EvalMaxSAT has no budget, so its
solve runs in a forked child process that is killed at the deadline, and a child
that does not finish is reported as a timeout. After the optimum is proven, the
runner emits the first optimal assignment, then, in a second forked child (so
that a failure there cannot lose the optimum already emitted), fixes the
objective at the optimum with a hard PB constraint in a fresh CaDiCaL instance
and enumerates the
rest of the optimal solutions, blocking the outputs as above. CaDiCaL supports only
a conflict budget, so its search runs in conflict-limited calls, and the clock
is checked between them.

Standard output is the protocol channel. EvalMaxSAT writes stray `c ...` lines
to file descriptor 1, so before any plugin loads, descriptor 1 is pointed at
descriptor 2 and the protocol is written to a saved copy of the original.

The default PB encoder recurses once per term, so a PB constraint over about a
thousand Bools overflows the default 8 MB stack and the process dies with
signal 11. The runner therefore raises its stack limit to the hard limit and
re-executes itself before doing anything else.
"""
import os
import resource
import sys

_SOFT, _HARD = resource.getrlimit(resource.RLIMIT_STACK)
if _SOFT != _HARD and os.environ.get("DCP_STACK_RAISED") != "1":
    resource.setrlimit(resource.RLIMIT_STACK, (_HARD, _HARD))
    os.environ["DCP_STACK_RAISED"] = "1"
    os.execv(sys.executable, [sys.executable] + sys.argv)

# Taken before any paramita import, because the plugins print to descriptor 1
# when they load and when EvalMaxSAT reports a hard-clause conflict.
_PROTOCOL = os.fdopen(os.dup(1), "w", buffering=1)
os.dup2(2, 1)
sys.stdout = _PROTOCOL

import contextlib  # noqa: E402
import functools  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import multiprocessing  # noqa: E402
from pathlib import Path  # noqa: E402
import signal  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402

sys.path.insert(0, "/opt/runner")
from runtime import emit, finish  # noqa: E402

from paramita.modelling import (  # noqa: E402
    Bool,
    BinaryIntegerOperation,
    BinaryOperation,
    DimacsVariablePool,
    PseudoBooleanOperation,
    UnaryIntegerOperation,
    UnaryOperation,
    add_to_container,
    add_to_weighted_container,
    evaluate,
    to_cnf,
)
from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver, SatSolver, SolvingBudget  # noqa: E402

SAT_SOLVER = "Cadical300"
MAXSAT_SOLVER = "EvalMaxSAT2022"

# Conflicts per CaDiCaL call. Small enough that the clock is checked often,
# large enough that the calls themselves are not the cost.
CONFLICT_CHUNK = 5000

# Time the runner's own deadline keeps ahead of the SIGALRM, so the runner
# reports its own timeout rather than losing a race to the signal.
SIGNAL_MARGIN = 0.5

# Time kept back from the deadline when waiting on EvalMaxSAT, so the runner
# can still report its own timeout rather than losing a race to SIGALRM.
MAXSAT_MARGIN = 0.5

BOOLEAN_EXPRESSIONS = (Bool, UnaryOperation, BinaryOperation, PseudoBooleanOperation)
INTEGER_EXPRESSIONS = (UnaryIntegerOperation, BinaryIntegerOperation)


class BudgetExceeded(Exception):
    """Raised by the SIGALRM handler, and by nothing a submission can raise."""


class Deadline:
    """The runner's own budget, ending a little before the SIGALRM that backs it up."""

    def __init__(self, request, started):
        self.limit = request["execution_timeout"] - SIGNAL_MARGIN
        self.started = started

    def left(self):
        return self.limit - (time.monotonic() - self.started)


def load(instance):
    spec = importlib.util.spec_from_file_location("candidate", "/input/model.py")
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        result = module.build(instance)
    if not isinstance(result, tuple) or len(result) not in (2, 3):
        raise ValueError("build(instance) must return (subject_to, outputs) or "
                         "(subject_to, outputs, objective)")
    subject_to, outputs = result[0], result[1]
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("build(instance) must return a nonempty output dictionary")
    objective = None
    if len(result) == 3:
        objective = result[2]
        if (not isinstance(objective, tuple) or len(objective) != 2
                or objective[0] not in ("minimize", "maximize")):
            raise ValueError('an objective must be ("minimize", expr) or ("maximize", expr)')
        if not is_integer_expression(objective[1]):
            raise ValueError("an objective must be a linear integer expression over Bools")
    return subject_to, outputs, objective


def is_integer_expression(node):
    return (isinstance(node, int) and not isinstance(node, bool)) or isinstance(node, INTEGER_EXPRESSIONS)


def as_list(subject_to):
    if isinstance(subject_to, (list, tuple)):
        return list(subject_to)
    return [subject_to]


def bool_names(node, found):
    """Every Bool name an expression, output or objective mentions."""
    if isinstance(node, Bool):
        found.add(node.name)
    elif isinstance(node, (list, tuple)):
        for value in node:
            bool_names(value, found)
    elif isinstance(node, dict):
        for value in node.values():
            bool_names(value, found)
    elif isinstance(node, (UnaryOperation, UnaryIntegerOperation)):
        bool_names(node.operand, found)
    elif isinstance(node, (BinaryOperation, BinaryIntegerOperation, PseudoBooleanOperation)):
        bool_names(node.lhs, found)
        bool_names(node.rhs, found)
    return found


def render(node, truth):
    """The declared outputs with their values under `truth`, a name -> bool map."""
    if isinstance(node, dict):
        return {name: render(value, truth) for name, value in node.items()}
    if isinstance(node, (list, tuple)):
        return [render(value, truth) for value in node]
    if isinstance(node, bool):
        return node
    if isinstance(node, int):
        return node
    if isinstance(node, BOOLEAN_EXPRESSIONS + INTEGER_EXPRESSIONS):
        value = evaluate(node, truth)
        if isinstance(value, bool) or isinstance(value, int):
            return value
        raise ValueError(f"an output evaluated to {type(value).__name__}")
    raise ValueError("an output leaf must be a Bool, a Boolean or integer expression, "
                     f"an int or a bool; got {type(node).__name__}")


class Assignment:
    """The truth of named Bools in one solver, read from its model."""

    def __init__(self, pool, model):
        self.pool = pool
        self.values = {abs(lit): lit > 0 for lit in model}

    def truth(self, names):
        # A variable the solver never saw is unconstrained, so any value is a
        # model; false is the one the runner reports.
        return {name: self.values.get(self.pool.get_variable(name), False) for name in names}


def blocking_clause(pool, names, truth):
    """Rule out exactly this combination of the named Bools."""
    clause = []
    for name in sorted(names):
        literal = pool.get_variable(name)
        clause.append(-literal if truth[name] else literal)
    return clause


def encode(pool, container, subject_to):
    for item in as_list(subject_to):
        add_to_container(item, to_cnf, container, pool)


def solve_within(solver, deadline):
    """CaDiCaL in conflict-limited calls, checking the clock between them.

    Returns True, False, or "timeout" once the deadline has passed.
    """
    while True:
        if deadline.left() <= 0:
            return "timeout"
        answer = solver.solve(budget=SolvingBudget(num_conflicts=CONFLICT_CHUNK))
        if answer is not None:
            return answer


def enumerate_models(solver, pool, outputs, names, request, deadline, seen, emitted):
    """Emit distinct declared outputs until the limit or exhaustion.

    `seen` holds the rendered outputs already emitted, and `emitted` counts
    them. Returns (emitted, status) where status is "limit", "exhausted" or
    "timeout".
    """
    limit = request["solution_limit"]
    while emitted < limit:
        answer = solve_within(solver, deadline)
        if answer == "timeout":
            return emitted, "timeout"
        if not answer:
            return emitted, "exhausted"
        truth = Assignment(pool, solver.model()).truth(names)
        values = render(outputs, truth)
        key = json.dumps(values, sort_keys=True)
        if key not in seen:
            seen.add(key)
            emit({"type": "solution", "values": values})
            emitted += 1
            if emitted >= limit:
                break
        clause = blocking_clause(pool, names, truth) if names else []
        if not clause:
            # The outputs depend on nothing the solver chooses, so there is no
            # second answer to look for.
            return emitted, "exhausted"
        solver.add_clause(clause)
    return emitted, "limit"


def satisfy(subject_to, outputs, request, deadline):
    solver = SatSolver.from_name(SAT_SOLVER)
    pool = DimacsVariablePool()
    encode(pool, solver, subject_to)
    names = sorted(bool_names(outputs, set()))
    emitted, status = enumerate_models(solver, pool, outputs, names, request, deadline, set(), 0)
    if status == "timeout":
        return finish("timeout", solve_seconds=deadline_spent(deadline))
    if status == "limit":
        return finish("limit", solve_seconds=deadline_spent(deadline))
    return finish("complete" if emitted else "unsat", solve_seconds=deadline_spent(deadline))


def deadline_spent(deadline):
    return time.monotonic() - deadline.started


def _maxsat_worker(solver, connection):
    """Runs in a forked child. EvalMaxSAT has no budget, so only a kill stops it."""
    try:
        answer = solver.solve()
        if answer == MAXSAT_ANSWER.OPTIMAL:
            connection.send((answer.name, solver.model(), solver.benefit()))
        else:
            connection.send((answer.name, None, None))
    except Exception as error:  # reported to the parent, which turns it into an error status
        connection.send(("ERROR", None, repr(error)))
    finally:
        connection.close()


def solve_maxsat(solver, deadline):
    """The proven optimum of a MaxSAT instance, or the status it stopped with.

    Returns (status, model, benefit). `status` is "OPTIMAL", "UNSATISFIABLE",
    or "timeout"; only OPTIMAL carries a model.
    """
    context = multiprocessing.get_context("fork")
    receiver, sender = context.Pipe(duplex=False)
    worker = context.Process(target=_maxsat_worker, args=(solver, sender))
    worker.start()
    sender.close()
    try:
        if not receiver.poll(max(deadline.left() - MAXSAT_MARGIN, 0.01)):
            return "timeout", None, None
        try:
            status, model, benefit = receiver.recv()
        except EOFError:
            return "ERROR", None, "the MaxSAT process ended without an answer"
        return status, model, benefit
    finally:
        if worker.is_alive():
            worker.kill()
        worker.join()
        receiver.close()


def optimise(subject_to, outputs, objective, request, deadline):
    direction, expression = objective
    # add_to_weighted_container maximises its argument.
    passed = expression if direction == "maximize" else -expression

    maxsat = MaxSatSolver.from_name(MAXSAT_SOLVER)
    pool = DimacsVariablePool()
    constant = add_to_weighted_container(
        obj=passed, subject_to=conjunction(subject_to), cnf_transformer=to_cnf,
        container=maxsat, var_pool=pool)
    status, model, benefit = solve_maxsat(maxsat, deadline)
    if status == "UNSATISFIABLE":
        return finish("unsat", solve_seconds=deadline_spent(deadline))
    if status == "ERROR":
        return finish("error", f"MaxSAT failed: {benefit}")
    if status != "OPTIMAL":
        # Not proven: nothing is reported, whatever state the solver stopped in.
        return finish("timeout", "the optimum was not proven", solve_seconds=deadline_spent(deadline))

    names = sorted(bool_names(outputs, bool_names(expression, set())))
    truth = Assignment(pool, model).truth(names)
    value = value_of(expression, truth)
    # Checks the direction and the encoding: the solver's benefit, plus the
    # constant it split off, must be the value of what was passed in.
    if benefit + constant != value_of(passed, truth):
        return finish("error", "the MaxSAT objective does not match the declared objective")

    seen = set()
    first = render(outputs, truth)
    seen.add(json.dumps(first, sort_keys=True))
    emit({"type": "solution", "values": first})
    emitted = 1
    if emitted >= request["solution_limit"]:
        return finish("limit", solve_seconds=deadline_spent(deadline))

    output_names = sorted(bool_names(outputs, set()))
    if not output_names:
        return finish("complete", solve_seconds=deadline_spent(deadline))
    # The rest of the optimal assignments, with the objective fixed at the
    # optimum. Encoding that equality can crash the PB encoder on a large
    # objective, so it runs in a forked child: a crash there loses only the
    # extra solutions, never the optimum already emitted.
    status = enumerate_optima(subject_to, outputs, expression, value, output_names,
                              {name: truth[name] for name in output_names},
                              request, deadline, seen, emitted)
    if status in ("timeout", "failed"):
        return finish("timeout", "the optimum was proven, the enumeration was not",
                      solve_seconds=deadline_spent(deadline))
    if status == "limit":
        return finish("limit", solve_seconds=deadline_spent(deadline))
    return finish("complete", solve_seconds=deadline_spent(deadline))


def _optima_worker(subject_to, outputs, expression, value, output_names, first,
                   request, deadline, seen, emitted, connection):
    """Runs in a forked child: sends ("solution", values) per new optimum, then
    ("status", status)."""
    def send_emit(record):
        connection.send(("solution", record["values"]))
    try:
        global emit
        emit = send_emit
        fixed = SatSolver.from_name(SAT_SOLVER)
        fixed_pool = DimacsVariablePool()
        encode(fixed_pool, fixed, subject_to)
        encode(fixed_pool, fixed, expression == value)
        fixed.add_clause(blocking_clause(fixed_pool, output_names, first))
        _, status = enumerate_models(fixed, fixed_pool, outputs, output_names, request,
                                     deadline, seen, emitted)
        connection.send(("status", status))
    except Exception as error:  # reported to the parent as a failed enumeration
        connection.send(("status", f"failed: {error!r}"))
    finally:
        connection.close()


def enumerate_optima(subject_to, outputs, expression, value, output_names, first,
                     request, deadline, seen, emitted):
    """Further optimal solutions from a forked child; the parent emits them.

    Returns "limit", "exhausted", "timeout", or "failed" (the child crashed or
    raised)."""
    context = multiprocessing.get_context("fork")
    receiver, sender = context.Pipe(duplex=False)
    worker = context.Process(target=_optima_worker, args=(
        subject_to, outputs, expression, value, output_names, first,
        request, deadline, seen, emitted, sender))
    worker.start()
    sender.close()
    try:
        while True:
            if not receiver.poll(max(deadline.left(), 0.01)):
                return "timeout"
            try:
                kind, payload = receiver.recv()
            except EOFError:
                return "failed"
            if kind == "solution":
                emit({"type": "solution", "values": payload})
            else:
                return "failed" if payload.startswith("failed") else payload
    finally:
        if worker.is_alive():
            worker.kill()
        worker.join()
        receiver.close()


def value_of(node, truth):
    return node if isinstance(node, int) else evaluate(node, truth)


def conjunction(subject_to):
    """One expression for a list of constraints, for add_to_weighted_container."""
    items = []
    for item in as_list(subject_to):
        if item is True:
            continue
        if item is False:
            return False
        items.append(item)
    if not items:
        return True
    return functools.reduce(lambda left, right: left & right, items)


def main():
    request = json.loads(Path("/input/request.json").read_text())
    if request.get("legacy"):
        return finish("unsupported", "This integration has no legacy submission format")

    def expired(signum, frame):
        raise BudgetExceeded("Runner execution budget exceeded")

    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, request["execution_timeout"])

    started = time.monotonic()
    deadline = Deadline(request, started)
    subject_to, outputs, objective = load(request["instance"])
    if objective is None:
        return satisfy(subject_to, outputs, request, deadline)
    return optimise(subject_to, outputs, objective, request, deadline)


if __name__ == "__main__":
    try:
        main()
    except BudgetExceeded as error:
        # SIGALRM fired while the submission was still building, or while a
        # solver was being waited on. Either way the budget ran out.
        finish("timeout", str(error))
    except Exception as error:
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))
