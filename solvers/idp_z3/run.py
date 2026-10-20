"""Runner protocol for the idp_z3 integration. Runs inside the image only.

A submission is a plain FO(.) knowledge base (`vocabulary` + `theory`, optionally
its own `structure`), not a program, and is parsed as written. All instance data
arrives in a `structure` the runner generates, which is how FO(.) hands data to a
knowledge base. FO(.) type ranges must be integer literals, so that structure also
interprets the types the data sizes:

- Every instance field whose name matches a declared symbol is interpreted: a
  scalar as `n := 5.`, an array as `cost := {(0,0)->1, ...}.` with 0-based
  indices, a Boolean array as the set of its true tuples.
- An argument type of such a symbol that is declared `<: Int` and interpreted
  nowhere is sized from the array: `type Task <: Int` with `cost: Task * Person
  -> Int` and a 4x5 `cost` gives `Task := {0..3}. Person := {0..4}.`
- A type `Range_f` declared `<: Int` and interpreted nowhere, for an integer scalar
  field `f`, is `{1..f}`: `type Range_n <: Int` with `n: 8` gives `Range_n := {1..8}.`
- Any other such type `T` with a declared constant `T_size: () -> Int` is `{1..v}`,
  where `v` is the value the theory gives `T_size` from the data
  (`T_size() = 2 * k().`). The runner reads it from IDP-Z3's own simplification of
  the theory, with `T` provisionally empty, before solving.

An output declared as a partial function, `diffs: Range_n -> Int (domain: gap)`, is
read only on the argument tuples where its domain predicate holds, so its length can
be shorter than its argument type.
- A ragged list of rows `F` binds padded with 0 (false) to the longest row, as a
  rectangular `F`, plus `F_len` with each row's real length. A list of mixed rows
  such as `[target, [cells...]]` binds one piece per column, `F_1`, `F_2`, ... (see
  `pieces`). Only the names a model declares are bound; a string is refused only in
  a declared field.

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

# The engine prints diagnostics to stdout, which is also the protocol channel. The
# protocol keeps the original stdout; everything else goes to stderr. Only the runner
# (`__main__`) redirects it: generation.next_work loads this file on the host to ask
# refusal(), which needs neither the engine nor a redirected stdout.
PROTOCOL = sys.stdout
if __name__ == "__main__":
    sys.stdout = sys.stderr

try:
    import z3  # noqa: E402
    from idp_engine import IDP, Theory  # noqa: E402
except ImportError:
    if __name__ == "__main__":
        raise
    z3 = IDP = Theory = None


def emit(record):
    print(json.dumps(record, allow_nan=False), file=PROTOCOL, flush=True)


def finish(status, detail="", **metadata):
    emit({"type": "status", "status": status, "detail": detail, **metadata})

INPUT = Path("/input")
DIRECTIONS = ("minimize", "maximize")
RANGE = "Range_"
SIZE = "_size"
INT_SET = "ℤ"
BOOL_SET = "𝔹"


class Unsupported(Exception):
    pass


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


def layout(value):
    """(dimensions, scalar kinds) of a rectangular list or scalar, else None."""
    if not isinstance(value, list):
        return (), {scalar_kind(value)}
    parts = [layout(item) for item in value]
    if any(part is None for part in parts) or len({part[0] for part in parts}) > 1:
        return None
    return (len(value),) + (parts[0][0] if parts else ()), set().union(*(part[1] for part in parts))


def scalar_kind(value):
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    return type(value).__name__


def column_class(column):
    classes = {"array" if isinstance(item, list) else scalar_kind(item) for item in column}
    return classes.pop() if len(classes) == 1 else None


def rows_of(value):
    return bool(value) and all(isinstance(row, list) for row in value)


def uniform(items):
    """(dimensions, kind) when every item has one shape and one scalar kind, else None."""
    if not items:
        return None
    shapes = [layout(item) for item in items]
    if any(found is None for found in shapes) or len({found[0] for found in shapes}) != 1:
        return None
    kinds = set().union(*(found[1] for found in shapes))
    return (shapes[0][0], kinds.pop()) if len(kinds) == 1 else None


def filled(dimensions, value):
    if not dimensions:
        return value
    return [filled(dimensions[1:], value) for _ in range(dimensions[0])]


def pieces(name, value, split=True):
    """The (key, rectangular value) pairs one instance field binds as, by these rules:

    1. A rectangular list binds unchanged; a list of rows also gives `<name>_len`.
    2. A ragged list of rows whose items share one shape and one scalar kind binds
       padded with 0 (False) to the longest row, plus `<name>_len`.
    3. Rows of one length whose columns differ in type bind one piece per column,
       `<name>_1`, `<name>_2`, ..., each by rules 1 and 2 without splitting again.
    4. Rows of unequal length whose first items are scalars bind as `<name>_1` (the
       first items) and `<name>_2` (the rest of each row, by rule 2).

    Anything else raises Unsupported. Strings and floats are not a shape problem here:
    literal() refuses them only in a field the model declares."""
    if not isinstance(value, list):
        return [(name, value)]
    shape = layout(value)
    if shape is not None and len(shape[1]) <= 1:
        return [(name, value)] + ([(f"{name}_len", [len(row) for row in value])]
                                  if rows_of(value) else [])
    if rows_of(value):
        found = uniform([item for row in value for item in row])
        if found is not None:
            dims, kind = found
            longest = max(len(row) for row in value)
            pad = filled(dims, False if kind == "bool" else 0)
            return [(name, [row + [pad] * (longest - len(row)) for row in value]),
                    (f"{name}_len", [len(row) for row in value])]
        width = len(value[0])
        if split and width and all(len(row) == width for row in value):
            columns = [[row[j] for row in value] for j in range(width)]
            classes = [column_class(column) for column in columns]
            if None not in classes and len(set(classes)) > 1:
                return [piece for j, column in enumerate(columns, 1)
                        for piece in pieces(f"{name}_{j}", column, split=False)]
        heads = [row[0] for row in value] if all(value) else []
        if split and heads and column_class(heads) not in (None, "array"):
            return (pieces(f"{name}_1", heads, split=False)
                    + pieces(f"{name}_2", [row[1:] for row in value], split=False))
    raise Unsupported(f"Instance field `{name}` is ragged or mixes types in a way this integration "
                      "cannot bind: only the shapes in the rules of pieces() are reshaped")


def refusal(name, value):
    """Why no model could bind this instance field, or None. generation.next_work asks
    this on the host for every instance field, so it never needs the engine."""
    try:
        pieces(name, value)
    except Unsupported as error:
        return str(error)
    return None


def bound_symbol(vocab, taken, name):
    decl = vocab.symbol_decls.get(name)
    return decl is not None and name not in taken and type(decl).__name__ == "SymbolDeclaration"


def open_type(vocab, taken, sort):
    """A type declared `<: Int` that neither the vocabulary nor a model structure interprets."""
    decl = vocab.symbol_decls.get(sort)
    return (decl is not None and type(decl).__name__ == "TypeDeclaration" and decl.interpretation is None
            and sort not in taken and str(decl.super_set) == INT_SET)


def bind(idp, instance):
    """The generated structure interpreting declared data symbols and index types. Only
    the pieces a model declares are bound: an undeclared field is never refused."""
    vocab_name, vocab = vocabulary(idp)
    taken = interpreted_by_model(idp)
    fields, origin = {}, {}
    for name, value in instance.items():
        try:
            parts = pieces(name, value)
        except Unsupported:
            if bound_symbol(vocab, taken, name):
                raise
            continue
        for key_name, data in parts:
            if key_name in fields and bound_symbol(vocab, taken, key_name):
                raise Unsupported(f"instance fields `{origin[key_name]}` and `{name}` both bind "
                                  f"as `{key_name}`")
            fields[key_name], origin[key_name] = data, name
    lines, sizes = [], {}
    for name, value in fields.items():
        if not bound_symbol(vocab, taken, name):
            continue
        decl = vocab.symbol_decls[name]
        dims = shape(value)
        if dims is None:
            raise Unsupported(f"instance field {name} is ragged and cannot be bound")
        sorts = [str(sort) for sort in decl.sorts]
        if len(sorts) != len(dims):
            raise ValueError(f"{name} is declared with {len(sorts)} arguments but the instance "
                             f"field has {len(dims)} dimensions")
        for sort, size in zip(sorts, dims):
            if open_type(vocab, taken, sort):
                if sort.startswith(RANGE):
                    raise ValueError(f"type {sort} is {{1..{sort[len(RANGE):]}}}, so it cannot index "
                                     f"the instance array {name}, whose indices start at 0")
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
    for sort in vocab.symbol_decls:
        if sort.startswith(RANGE) and open_type(vocab, taken, sort):
            field = sort[len(RANGE):]
            bound = instance.get(field)
            if isinstance(bound, bool) or not isinstance(bound, int):
                raise ValueError(f"type {sort} is {{1..{field}}}, but {field} is not an integer "
                                 "scalar field of the instance")
            lines.append(f"{sort} := {{1..{bound}}}." if bound >= 1 else f"{sort} := {{}}.")
    return f"structure _dcp_instance:{vocab_name} {{\n" + "\n".join(lines) + "\n}\n"


def sized(idp, source, structure):
    """`structure` plus `T := {1..v}.` for each open type T sized by a `T_size` constant."""
    _, vocab = vocabulary(idp)
    taken = interpreted_by_model(idp)
    pending = [sort for sort in vocab.symbol_decls
               if open_type(vocab, taken, sort) and not sort.startswith(RANGE)
               and sort + SIZE in vocab.symbol_decls
               and not re.search(rf"^{re.escape(sort)} := ", structure, re.M)]
    if not pending:
        return structure
    probe = structure.replace("\n}\n", "".join(f"\n{sort} := {{}}." for sort in pending) + "\n}\n")
    full = IDP.from_str(source + "\n" + probe)
    theory = Theory(*full.theories.values(), *full.structures.values())
    found = {}
    for sentence in theory.constraints:
        if type(sentence).__name__ != "AComparison" or len(sentence.sub_exprs) != 2:
            continue
        if [str(op) for op in getattr(sentence, "operator", [])] != ["="]:
            continue
        for symbol, value in (sentence.sub_exprs, sentence.sub_exprs[::-1]):
            if (type(symbol).__name__ == "AppliedSymbol" and not symbol.sub_exprs
                    and type(getattr(value, "py_value", None)) is int):
                found.setdefault(symbol.decl.name, value.py_value)
    for assignment in theory.assignments.values():
        sentence, value = assignment.sentence, assignment.value
        if (type(sentence).__name__ == "AppliedSymbol" and not sentence.sub_exprs
                and type(getattr(value, "py_value", None)) is int):
            found.setdefault(sentence.decl.name, value.py_value)
    lines = []
    for sort in pending:
        size = found.get(sort + SIZE)
        if size is None:
            raise ValueError(f"type {sort} is sized by {sort}{SIZE}, which the theory must define "
                             f"from instance data alone, as `{sort}{SIZE}() = <expression>.`")
        lines.append(f"{sort} := {{1..{size}}}." if size >= 1 else f"{sort} := {{}}.")
    return structure.replace("\n}\n", "".join("\n" + line for line in lines) + "\n}\n")


def domain_tests(theory, vocab, name):
    """For an output declared `(domain: p)`, a function from argument tuple to the ground
    atoms that must hold for the tuple to be part of the output; None for a total output."""
    decl = vocab.symbol_decls[name]
    domains, sorts = [str(domain) for domain in decl.domains], [str(sort) for sort in decl.sorts]
    if domains == sorts:
        return None
    if len(domains) == len(sorts):
        atoms = [None if domain == sort else output_terms(theory, domain)
                 for domain, sort in zip(domains, sorts)]
        return lambda index: [atom[(item,)] for atom, item in zip(atoms, index) if atom is not None]
    atoms = output_terms(theory, domains[0])
    return lambda index: [atoms[index]]


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


def literal_argument(name, argument, theory):
    """The Python value of a ground sentence's argument, reduced through the model's
    interpretation when the engine has not already simplified it to a literal."""
    value = getattr(argument, "py_value", None)
    if value is not None:
        return value
    try:
        reduced = z3.simplify(argument.translate(theory))
    except Exception as error:
        raise ValueError(f"Declared output {name} has an argument {argument} that cannot be "
                         f"read from the model: {error}")
    if z3.is_int_value(reduced):
        return reduced.as_long()
    if z3.is_true(reduced) or z3.is_false(reduced):
        return z3.is_true(reduced)
    raise ValueError(f"Declared output {name} has a ground sentence whose argument {argument} "
                     "does not reduce to a value in the model")


def output_terms(theory, name):
    """The ground terms of declared output `name`, keyed by argument tuple."""
    terms = {}
    for assignment in theory.assignments.values():
        sentence = assignment.sentence
        if type(sentence).__name__ == "AppliedSymbol" and sentence.decl.name == name:
            arguments = tuple(literal_argument(name, argument, theory) for argument in sentence.sub_exprs)
            try:
                terms[arguments] = sentence.translate(theory)
            except Exception as error:
                raise ValueError(f"Declared output {name} has a ground sentence that cannot be "
                                 f"translated: {error}")
    if not terms:
        raise ValueError(f"Declared output {name} is not a symbol of the vocabulary")
    return terms


def nest(values):
    """{(i, j): v} with a rectangular index set -> nested lists in ascending order."""
    if not values:
        return []
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
        idp = IDP.from_str(source)
        full = IDP.from_str(source + "\n" + sized(idp, source, bind(idp, instance)))
        _, vocab = vocabulary(full)
        theory = Theory(*full.theories.values(), *full.structures.values())
    return theory, vocab, objective(vocab)


def solve(request):
    deadline = time.monotonic() + request["execution_timeout"]
    theory, vocab, goal = load(request)
    outputs = {name: output_terms(theory, name) for name in request["outputs"]}
    domains = {name: domain_tests(theory, vocab, name) for name in request["outputs"]}
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

    count = 0
    while count < request["solution_limit"]:
        status = check(solver, deadline)
        if status == z3.unsat:
            return finish("complete" if count else "unsat")
        if status != z3.sat:
            return finish("timeout")
        model = solver.model()

        def holds(atom):
            return z3.is_true(model.eval(atom, model_completion=True))
        shown = {name: {index: term for index, term in terms_.items()
                        if domains[name] is None or all(map(holds, domains[name](index)))}
                 for name, terms_ in outputs.items()}
        values = {name: nest({index: python(model.eval(term, model_completion=True))
                              for index, term in terms_.items()})
                  for name, terms_ in shown.items()}
        terms = [term for terms_ in shown.values() for term in terms_.values()]
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
