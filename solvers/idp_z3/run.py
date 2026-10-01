"""Runner protocol for the idp_z3 integration. Runs inside the image only.

A submission is a plain FO(.) knowledge base (`vocabulary` + `theory`, optionally
its own `structure`), not a program. The runner binds the instance into it:

- Every `${name}` in the source is replaced by the instance's integer scalar
  field `name`. FO(.) type ranges must be integer literals, so this is the only
  way to write `type Row := {1..${n}}`. `$` is otherwise only legal in FO(.)
  directly before `(`, so the marker cannot collide with real syntax.
- Every instance field whose name matches a declared symbol is interpreted in a
  generated `structure`: a scalar as `n := 5.`, an array as `cost := {(0,0)->1, ...}.`
  with 0-based indices, a Boolean array as the set of its true tuples.
- An argument type of such a symbol that is declared `<: Int` and interpreted
  nowhere is sized from the array: `type Task <: Int` with `cost: Task * Person
  -> Int` and a 4x5 `cost` gives `Task := {0..3}. Person := {0..4}.`

A nullary `minimize: () -> Int` or `maximize: () -> Int` makes it an optimization.

The runner drives `theory.solver` (a z3.Solver) and `theory.optimize_solver` (a
z3.Optimize) itself rather than calling `Theory.expand` / `Theory.optimize`:
`expand` blocks on every unknown atom, so auxiliary symbols multiply the models,
and treats a z3 `unknown` like `unsat`; `optimize` raises the same AssertionError
for an unsatisfiable theory and for a timeout. Here only the declared outputs are
blocked, and `unknown` is always reported as a timeout, never as exhaustion.
"""
import contextlib
import json
from pathlib import Path
import re
import signal
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, finish  # noqa: E402

import z3  # noqa: E402
from idp_engine import IDP, Theory  # noqa: E402

INPUT = Path("/input")
TEMPLATE = re.compile(r"\$\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}")
DIRECTIONS = ("minimize", "maximize")
INT_SET = "ℤ"
BOOL_SET = "𝔹"


class Unsupported(Exception):
    pass


def substitute(source, instance):
    def replace(match):
        name = match.group(1)
        if name not in instance:
            raise ValueError(f"${{{name}}} names no instance field")
        value = instance[name]
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"${{{name}}} must name an integer scalar field, not {type(value).__name__}")
        return str(value)
    result = TEMPLATE.sub(replace, source)
    leftover = re.search(r"\$\{[^}]*\}", result)
    if leftover:
        raise ValueError(f"{leftover.group(0)}: a placeholder takes one integer field name, not an expression")
    return result


def shape(value):
    """Dimensions of a rectangular list, or None for a ragged one."""
    if not isinstance(value, list):
        return ()
    if not value:
        return (0,)
    inner = {shape(item) for item in value}
    if len(inner) != 1 or None in inner:
        return None
    return (len(value),) + inner.pop()


def cells(value, prefix=()):
    if not isinstance(value, list):
        yield prefix, value
        return
    for index, item in enumerate(value):
        yield from cells(item, prefix + (index,))


def literal(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    raise Unsupported(f"instance values of type {type(value).__name__} cannot be bound into FO(.)")


def key(index):
    return str(index[0]) if len(index) == 1 else "(" + ",".join(map(str, index)) + ")"


def vocabulary(idp):
    if len(idp.vocabularies) != 1:
        raise ValueError("A submission must declare exactly one vocabulary")
    return next(iter(idp.vocabularies.items()))


def interpreted_by_model(idp):
    names = set()
    for structure in idp.structures.values():
        names.update(str(name) for name in structure.interpretations)
    return names


def bind(idp, instance):
    """The generated structure interpreting declared data symbols and index types."""
    vocab_name, vocab = vocabulary(idp)
    taken = interpreted_by_model(idp)
    lines, sizes = [], {}
    for name, value in instance.items():
        decl = vocab.symbol_decls.get(name)
        if decl is None or name in taken or type(decl).__name__ != "SymbolDeclaration":
            continue
        dims = shape(value)
        if dims is None:
            raise Unsupported(f"instance field {name} is ragged and cannot be bound")
        sorts = [str(sort) for sort in decl.sorts]
        if len(sorts) != len(dims):
            raise ValueError(f"{name} is declared with {len(sorts)} arguments but the instance "
                             f"field has {len(dims)} dimensions")
        for sort, size in zip(sorts, dims):
            sort_decl = vocab.symbol_decls.get(sort)
            if (sort_decl is not None and sort_decl.interpretation is None and sort not in taken
                    and str(sort_decl.super_set) == INT_SET):
                if sizes.setdefault(sort, size) != size:
                    raise ValueError(f"type {sort} would be sized both {sizes[sort]} and {size}")
        boolean = str(decl.codomain) == BOOL_SET
        if not dims:
            lines.append(f"{name} := {literal(value)}.")
        elif boolean:
            true = [key(index) for index, item in cells(value) if literal(item) == "true"]
            lines.append(f"{name} := {{{', '.join(true)}}}.")
        else:
            pairs = [f"{key(index)}->{literal(item)}" for index, item in cells(value)]
            lines.append(f"{name} := {{{', '.join(pairs)}}}.")
    for sort, size in sizes.items():
        lines.append(f"{sort} := {{0..{size - 1}}}." if size else f"{sort} := {{}}.")
    return f"structure _dcp_instance:{vocab_name} {{\n" + "\n".join(lines) + "\n}\n"


def objective(vocab):
    found = [(name, vocab.symbol_decls[name]) for name in DIRECTIONS if name in vocab.symbol_decls]
    if not found:
        return None
    if len(found) > 1:
        raise ValueError("Declare either minimize or maximize, not both")
    name, decl = found[0]
    codomain = str(decl.codomain)
    numeric = codomain == INT_SET or str(getattr(vocab.symbol_decls.get(codomain), "super_set", "")) == INT_SET
    if decl.sorts or not numeric:
        raise ValueError(f"{name} must be a nullary integer function: {name}: () -> Int")
    return name


def output_terms(theory, name):
    """The ground terms of declared output `name`, keyed by argument tuple."""
    terms = {}
    for assignment in theory.assignments.values():
        sentence = assignment.sentence
        if type(sentence).__name__ == "AppliedSymbol" and sentence.decl.name == name:
            arguments = tuple(argument.py_value for argument in sentence.sub_exprs)
            terms[arguments] = sentence.translate(theory)
    if not terms:
        raise ValueError(f"Declared output {name} is not a symbol of the vocabulary")
    return terms


def nest(values):
    """{(i, j): v} with a rectangular index set -> nested lists in ascending order."""
    arity = len(next(iter(values)))
    if arity == 0:
        return values[()]
    axes = [sorted({index[axis] for index in values}) for axis in range(arity)]

    def build(prefix, axis):
        if axis == arity:
            return values[prefix]
        return [build(prefix + (item,), axis + 1) for item in axes[axis]]
    expected = 1
    for axis in axes:
        expected *= len(axis)
    if expected != len(values):
        raise ValueError("A declared output must be total over its argument types")
    return build((), 0)


def python(value):
    if z3.is_true(value):
        return True
    if z3.is_false(value):
        return False
    if z3.is_int_value(value):
        return value.as_long()
    raise ValueError(f"Declared outputs must be integer or Boolean, got {value}")


def remaining_ms(deadline):
    left = deadline - time.monotonic()
    return None if left <= 0 else max(1, int(left * 1000))


def check(solver, deadline):
    budget = remaining_ms(deadline)
    if budget is None:
        return None
    solver.set("timeout", budget)
    return solver.check()


def load(request):
    source = (INPUT / "model.idp").read_text()
    instance = request["instance"]
    with contextlib.redirect_stdout(sys.stderr):
        source = substitute(source, instance)
        idp = IDP.from_str(source)
        full = IDP.from_str(source + "\n" + bind(idp, instance))
        _, vocab = vocabulary(full)
        theory = Theory(*full.theories.values(), *full.structures.values())
    return theory, objective(vocab)


def solve(request):
    deadline = time.monotonic() + request["execution_timeout"]
    theory, goal = load(request)
    outputs = {name: output_terms(theory, name) for name in request["outputs"]}
    solver = theory.solver
    solver.push()
    theory._add_assignment(solver)

    if goal is not None:
        target = output_terms(theory, goal)[()]
        optimizer = theory.optimize_solver
        optimizer.push()
        theory._add_assignment(optimizer)
        handle = (optimizer.minimize if goal == "minimize" else optimizer.maximize)(target)
        status = check(optimizer, deadline)
        if status == z3.unsat:
            return finish("unsat")
        if status != z3.sat:
            return finish("timeout", "Candidate optimum was not proven")
        # For an unbounded objective z3 still answers sat, and model().eval gives
        # the witness model's value rather than the bound; only lower == upper,
        # both finite, is a proven optimum.
        low, high = optimizer.lower(handle), optimizer.upper(handle)
        optimizer.pop()
        if not (z3.is_int_value(low) and z3.is_int_value(high)):
            return finish("error", f"The objective is unbounded: between {low} and {high}")
        if low.as_long() != high.as_long():
            return finish("timeout", "Candidate optimum was not proven")
        best = low
        # Enumerate only assignments achieving the proven optimum.
        solver.add(target == best)

    terms = [term for values in outputs.values() for term in values.values()]
    count = 0
    while count < request["solution_limit"]:
        status = check(solver, deadline)
        if status == z3.unsat:
            return finish("complete" if count else "unsat")
        if status != z3.sat:
            return finish("timeout")
        model = solver.model()
        values = {name: nest({index: python(model.eval(term, model_completion=True))
                              for index, term in terms_.items()})
                  for name, terms_ in outputs.items()}
        emit({"type": "solution", "values": values})
        count += 1
        if count == request["solution_limit"]:
            break
        solver.add(z3.Or([term != model.eval(term, model_completion=True) for term in terms]))
    finish("limit")


def main():
    try:
        request = json.loads((INPUT / "request.json").read_text())
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by idp_z3")

        def expired(signum, frame):
            raise TimeoutError("Runner execution budget exceeded")

        signal.signal(signal.SIGALRM, expired)
        signal.setitimer(signal.ITIMER_REAL, request["execution_timeout"] + 5)
        solve(request)
    except TimeoutError:
        finish("timeout")
    except Unsupported as error:
        finish("unsupported", str(error))
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error).strip().splitlines()[-1] if str(error).strip() else type(error).__name__)


if __name__ == "__main__":
    main()
