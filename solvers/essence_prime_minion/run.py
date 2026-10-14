"""Essence' through Savile Row 1.11.1 to Minion, with the instance binding this integration adds.

The JSON instance becomes an Essence' parameter file. Only the fields the model
declares with `given` are bound, as `letting NAME = VALUE`: an instance field no
`given` names is ignored, whatever its type, so string metadata such as `name`
or `note` never reaches Savile Row. A declared given with no value is refused.
A model that needs a size which varies per instance declares `F_dim1`, `F_dim2`,
... beside a list field `F`; they bind the length along each axis of F after
reshaping. Matrices are indexed from 1, Booleans are `true`/`false`. Essence' has
no strings or floats and a matrix literal must be rectangular, so a declared
field is bound by these rules:

1. An int, a Boolean, or a rectangular list of them binds unchanged. When it is a
   nonempty list of lists, `<field>_len` (each row's length) is available beside it.
2. A ragged list of rows whose items all have one shape and whose scalars all
   have one type binds as `<field>`, padded to the longest row with 0 or false,
   plus `<field>_len`. `<field>_dim1` is the outer length and `<field>_dim2` the
   padded longest row.
3. A list of equal-length rows whose columns have different types binds as one
   matrix per column, `<field>_1`, `<field>_2`, ...; `<field>` itself is not
   bound. Each column then binds by rule 1 or 2, but is not split again.
4. `<field>_dimK` (K from 1) is the length of a bound list along axis K, for every
   list bound by rules 1 to 3.
5. Anything else that is declared is refused: floats, strings, empty lists, names
   that are not Essence' identifiers, ragged or mixed fields outside rules 2 and 3.

Essence' reserved words cannot be names, so a field or output named `matrix` is
declared as `matrix_` (`given matrix_ : ...`, `find matrix_ : ...`). It binds under
that name, and a solution value `matrix_` is reported as `matrix`.

A refusal is an `error` status with the reason as detail.

Savile Row runs from a fresh directory under /tmp. The solutions of every
`find` variable are read back from its solution files. Optimisation reports a
solution only when Minion finished its search (`SolverTimeOut:0`); Minion's info
file has no separate optimality key.
"""
import glob
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, "/opt/runner")
import runtime

SAVILEROW = "/opt/savilerow"
# Essence' and Savile Row words. A field or output with one of these names is written
# `<name>_` in the model, and binds or reads back under that name.
RESERVED = {"forall", "forAll", "exists", "sum", "such", "that", "letting", "given", "where",
            "find", "language", "int", "bool", "union", "intersect", "in", "false", "true",
            "matrix", "indexed", "by", "of", "be", "domain", "minimising", "maximising",
            "branching", "on", "heuristic", "toInt", "flatten", "table", "alldiff", "allDiff"}
GIVEN = re.compile(r"(?m)^[ \t]*given[ \t]+([^:\n]*):")
# Objective bounds for the auxiliary variable used to read the optimum back.
BIG = 10 ** 12


class Unbindable(ValueError):
    pass


def kind(value):
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    return "float" if isinstance(value, float) else "string" if isinstance(value, str) else "other"


def layout(value):
    """(dimensions, scalar kinds) of a rectangular array or scalar, else None."""
    if not isinstance(value, list):
        return (), {kind(value)}
    parts = [layout(item) for item in value]
    if any(part is None for part in parts) or len({part[0] for part in parts}) > 1:
        return None
    inner = parts[0][0] if parts else ()
    return (len(value),) + inner, set().union(*(part[1] for part in parts))


def leaves(value):
    if isinstance(value, list):
        return [leaf for item in value for leaf in leaves(item)]
    return [value]


def filled(dimensions, value):
    if not dimensions:
        return value
    return [filled(dimensions[1:], value) for _ in range(dimensions[0])]


def column_class(column):
    kinds = {"array" if isinstance(item, list) else kind(item) for item in column}
    return kinds.pop() if len(kinds) == 1 else None


def field(name, value, split=True):
    """Yield (name, value, required) bindings for one instance field. Derived
    names (`_len`) are never required: they bind only when a given declares them."""
    if not isinstance(value, list):
        yield name, value, True
        return
    rows = bool(value) and all(isinstance(row, list) for row in value)
    shape = layout(value)
    if shape is not None and len(shape[1]) <= 1:
        yield name, value, True
        if rows:
            yield f"{name}_len", [len(row) for row in value], False
        return
    if rows:
        items = [item for row in value for item in row]
        shapes = [layout(item) for item in items]
        if (items and None not in shapes and len({s[0] for s in shapes}) == 1
                and len(set().union(*(s[1] for s in shapes))) == 1):
            longest = max(len(row) for row in value)
            pad = filled(shapes[0][0], False if kind(leaves(items)[0]) == "bool" else 0)
            yield name, [row + [pad] * (longest - len(row)) for row in value], True
            yield f"{name}_len", [len(row) for row in value], False
            return
        width = len(value[0])
        if split and width and all(len(row) == width for row in value):
            columns = [[row[j] for row in value] for j in range(width)]
            classes = [column_class(column) for column in columns]
            if None not in classes and len(set(classes)) > 1:
                for j, column in enumerate(columns, 1):
                    yield from field(f"{name}_{j}", column, split=False)
                return
    raise Unbindable(
        f"Instance field `{name}` is ragged or mixes types in a way this integration "
        "cannot bind: only a ragged list of rows with one item shape and one scalar "
        "type, or equal-length rows whose columns differ in type, are reshaped")


def bindings(name, value):
    """field(), plus `<key>_dim1`, `<key>_dim2`, ... (the length along each axis of
    every required list, after reshaping) as optional bindings."""
    for key, data, needed in field(name, value):
        yield key, data, needed
        shape = layout(data) if needed and isinstance(data, list) else None
        for axis, length in enumerate(shape[0] if shape else (), 1):
            yield f"{key}_dim{axis}", length, False


def declared_givens(source):
    """Names declared by `given` lines, comma-separated lists included, comments ignored."""
    names = []
    for match in GIVEN.finditer(comment_free(source)):
        names += [part.strip() for part in match.group(1).split(",") if part.strip()]
    return names


def escape(name):
    """The Essence' name a field binds under: a reserved word gets a trailing `_`."""
    return name + "_" if name in RESERVED else name


def unescape(name):
    return name[:-1] if name.endswith("_") and name[:-1] in RESERVED else name


def bind(instance, declared):
    """The bindings the model declares, by canonical name. Fields and derived names
    the model does not declare are never bound, so they cannot be refused."""
    wanted = {unescape(name) for name in declared}
    relevant = {name: value for name, value in instance.items()
                if name in wanted or any(d.startswith(name + "_") for d in wanted)}
    required, optional = {}, {}
    for name, value in relevant.items():
        for key, data, needed in bindings(name, value):
            if not needed:
                optional[key] = data
                continue
            if key in required or (key != name and key in instance):
                raise Unbindable(f"Instance field `{name}` binds as `{key}`, which is already "
                                 "an instance field or another generated name")
            required[key] = data
    for key, data in optional.items():
        if key in wanted and key not in instance and key not in required:
            required[key] = data
    return {key: data for key, data in required.items() if key in wanted}


def refusal(name, value):
    """Why run.py cannot reshape this instance field on its own, or None. For a caller
    that must know whether any model could be given the field, without a model. A
    string is not a reshaping problem: it is refused only when a model declares the
    field as a given (see literal()), so a model that ignores the field is unaffected."""
    try:
        list(bindings(name, value))
    except Unbindable as error:
        return str(error)
    return None


def literal(name, value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        if not value:
            raise Unbindable(f"Instance field `{name}` contains an empty list, which an "
                             "Essence' matrix literal cannot express")
        return "[" + ", ".join(literal(name, item) for item in value) + "]"
    raise Unbindable(f"Instance field `{name}` holds a {kind(value)} value; Essence' parameters "
                     "are integers, Booleans and matrices of them")


def param_file(instance, source, check=True):
    """The parameter file for the givens `source` declares. With `check`, a declared
    given that the instance does not provide is refused."""
    declared = declared_givens(source)
    values = bind(instance, declared)
    if check:
        missing = [name for name in dict.fromkeys(declared) if unescape(name) not in values]
        if missing:
            raise Unbindable("Declared given " + ", ".join(f"`{name}`" for name in missing)
                             + " has no value: the instance has no such field, and no field "
                             "it is a size of")
    lines = ["language ESSENCE' 1.0"]
    for name, value in values.items():
        escaped = escape(name)
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", escaped):
            raise Unbindable(f"Instance field `{name}` is not usable as an Essence' identifier")
        lines.append(f"letting {escaped} = {literal(name, value)}")
    return "\n".join(lines) + "\n"


# --- reading solutions ------------------------------------------------------

TOKEN = re.compile(r"\s*(-?\d+|true|false|\[|\]|,|;)")


def parse_value(text):
    """Parse an Essence' literal: int, Boolean or nested matrix; an index
    domain after `;` is skipped, as every matrix is read as a JSON list."""
    pos = 0

    def token():
        nonlocal pos
        match = TOKEN.match(text, pos)
        if not match:
            raise ValueError(f"Cannot parse solution value near {text[pos:pos + 30]!r}")
        pos = match.end()
        return match.group(1)

    def value():
        nonlocal pos
        first = token()
        if first == "[":
            items = []
            while True:
                if TOKEN.match(text, pos) and TOKEN.match(text, pos).group(1) == "]":
                    token()
                    return items
                items.append(value())
                follow = token()
                if follow == ";":
                    depth = 0
                    while True:  # skip the index domain up to the closing bracket
                        char = text[pos]
                        pos += 1
                        depth += char == "("
                        depth -= char == ")"
                        if char == "]" and depth <= 0:
                            return items
                elif follow == "]":
                    return items
                elif follow != ",":
                    raise ValueError("Malformed matrix in solution file")
        if first in ("true", "false"):
            return first == "true"
        return int(first)

    result = value()
    if text[pos:].strip():
        raise ValueError(f"Trailing text in solution value: {text[pos:pos + 30]!r}")
    return result


def parse_solution(text):
    text = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("$"))
    found = list(re.finditer(r"(?m)^letting\s+([A-Za-z][A-Za-z0-9_.]*)\s+(?:be|=)\s+", text))
    values = {}
    for i, match in enumerate(found):
        end = found[i + 1].start() if i + 1 < len(found) else len(text)
        values[match.group(1)] = parse_value(text[match.end():end].strip())
    return values


def read_info(path):
    info = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8", errors="replace"):
            key, _, value = line.partition(":")
            info[key.strip()] = value.strip()
    return info


# --- running Savile Row -----------------------------------------------------

OBJECTIVE = re.compile(r"(?m)^[ \t]*(minimising|maximising)[ \t]+(\S[^\n]*?)[ \t]*$")


def comment_free(source):
    return re.sub(r"\$[^\n]*", "", source)


def with_constraint(source, constraint):
    """Add one constraint after the model's last. Savile Row takes a single `such
    that` list, so a model that has one gets a comma, and one without gets the keyword."""
    if re.search(r"\bsuch\s+that\b", comment_free(source)):
        return source.rstrip() + f",\n{constraint}\n"
    return source.rstrip() + f"\nsuch that\n{constraint}\n"


def cells(value, prefix=()):
    """(1-based index, scalar) for every element of a solution value."""
    if isinstance(value, list):
        for position, item in enumerate(value, 1):
            yield from cells(item, prefix + (position,))
    else:
        yield prefix, value


def nogood(values):
    """A constraint that excludes one assignment of the declared outputs, matrices
    flattened to elements. None when there is nothing to exclude."""
    parts = []
    for name, value in values.items():
        for index, scalar in cells(value):
            target = escape(name) + (f"[{', '.join(map(str, index))}]" if index else "")
            literal = ("true" if scalar else "false") if isinstance(scalar, bool) else str(scalar)
            parts.append(f"{target} = {literal}")
    if not parts:
        return None
    conjunction = " /\\ ".join(parts)
    return "!(" + conjunction + ")"


def savile_row(work, source, param, deadline, count):
    """One Savile Row + Minion run. Returns (solutions, info, error). `solutions`
    is a list of dicts of every find variable; `count` caps them (`None` for an
    optimisation, which writes one)."""
    for old in glob.glob(os.path.join(work, "out*")) + glob.glob(os.path.join(work, ".MINION*")):
        os.remove(old)
    with open(os.path.join(work, "model.eprime"), "w", encoding="utf-8") as handle:
        handle.write(source)
    left = deadline - time.monotonic()
    if left <= 2:
        return None, {}, "timeout"
    seconds = max(1, int(left) - 2)
    command = ["java", "-XX:ParallelGCThreads=1", "-XX:+UseSerialGC", "-Xmx1200m",
               f"-Djava.library.path={SAVILEROW}/lib", "-jar", f"{SAVILEROW}/savilerow.jar",
               "model.eprime", "model.param", "-run-solver", "-minion-bin", f"{SAVILEROW}/bin/minion",
               "-timelimit", str(seconds), "-solver-options", f"-cpulimit {seconds}",
               "-out-solution", "out.solution", "-out-info", "out.info", "-out-minion", "out.minion",
               "-out-aux", "out.aux"]
    if count is not None:
        command += ["-num-solutions", str(count)]
    process = subprocess.Popen(command, cwd=work, stdout=sys.stderr, stderr=sys.stderr,
                               start_new_session=True)
    try:
        process.wait(timeout=max(1, left))
    except subprocess.TimeoutExpired:
        return None, {}, "timeout"
    finally:
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                shutil.rmtree(work, ignore_errors=True)
            process.wait()
    info = read_info(os.path.join(work, "out.info"))
    if info.get("SavileRowTimeOut") == "1":
        return None, info, "timeout"
    if process.returncode:
        return None, info, f"Savile Row exited {process.returncode}; see stderr"
    files = sorted(glob.glob(os.path.join(work, "out.solution*")))
    solutions = [parse_solution(open(path, encoding="utf-8").read()) for path in files]
    return [{unescape(name): value for name, value in solution.items()} for solution in solutions], info, None


def essence_solver(request):
    started = time.monotonic()
    deadline = started + request["execution_timeout"]
    source = open("/input/model.eprime", encoding="utf-8").read()
    work = tempfile.mkdtemp(prefix="essence_", dir="/tmp")
    try:
        param = param_file({} if request["legacy"] else request["instance"], source,
                           check=not request["legacy"])
        with open(os.path.join(work, "model.param"), "w", encoding="utf-8") as handle:
            handle.write(param)
        run(request, source, work, deadline)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def run(request, source, work, deadline):
    limit = request["solution_limit"]
    declared = request.get("outputs") or []
    seen, emitted = set(), []

    def project(solution):
        if declared and all(name in solution for name in declared):
            return {name: solution[name] for name in declared}
        return solution

    def keep(solutions):
        for solution in solutions:
            values = project(solution)
            key = json.dumps(values, sort_keys=True)
            if key not in seen:
                seen.add(key)
                emitted.append(values)

    def flush(status, detail=""):
        for values in emitted[:limit]:
            runtime.emit({"type": "solution", "values": values})
        return runtime.finish(status, detail)

    objectives = OBJECTIVE.findall(comment_free(source))
    optimising = bool(re.search(r"\b(minimising|maximising)\b", comment_free(source)))
    if optimising:
        solutions, info, error = savile_row(work, source, None, deadline, None)
        if error == "timeout" or (not error and info.get("SolverTimeOut") != "0"):
            return runtime.finish("timeout", "Candidate optimum was not proven")
        if error:
            return runtime.finish("error", error)
        if not solutions:
            return runtime.finish("unsat")
        keep(solutions[:1])
        if limit == 1:
            return flush("limit")
        if len(objectives) != 1 or len(OBJECTIVE.findall(source)) != 1:
            return runtime.finish("unsupported", "Enumeration requires `minimising EXPR` or "
                                  "`maximising EXPR` on its own line")
        direction, expression = objectives[0]
        # Read the optimum through an auxiliary variable, then fix it.
        probe = OBJECTIVE.sub(lambda m: f"find dcp_objective_value : int({-BIG}..{BIG})\n"
                              f"{direction} dcp_objective_value", source, count=1)
        probe = with_constraint(probe, f"dcp_objective_value = ({expression})")
        solutions, info, error = savile_row(work, probe, None, deadline, None)
        if error == "timeout" or (not error and info.get("SolverTimeOut") != "0"):
            return flush("timeout", "Candidate optimum was not proven")
        if error:
            return runtime.finish("error", error)
        if not solutions or "dcp_objective_value" not in solutions[0]:
            return runtime.finish("error", "Could not read the optimum back from Savile Row")
        value = solutions[0]["dcp_objective_value"]
        source = with_constraint(OBJECTIVE.sub("", source, count=1), f"({expression}) = {value}")
    # Satisfaction, or an optimisation fixed at its proven optimum. Savile Row
    # enumerates every `find` variable, so an auxiliary one that the constraints
    # leave free repeats an output assignment. Each round asks for the solutions
    # still missing, and excludes every assignment found so far with a nogood, so
    # each round adds a new output assignment or shows that none remain.
    nogoods = []
    while True:
        want = limit - len(emitted)
        attempt = with_constraint(source, ",\n".join(nogoods)) if nogoods else source
        solutions, info, error = savile_row(work, attempt, None, deadline, want)
        if error == "timeout":
            return flush("timeout")
        if error:
            return runtime.finish("error", error)
        keep(solutions)
        if len(emitted) >= limit:
            return flush("limit")
        if info.get("SolverTimeOut") != "0":
            return flush("timeout")
        if len(solutions) < want:
            return flush("complete" if emitted else "unsat")
        for solution in solutions:
            text = nogood(project(solution))
            if text is None:
                return flush("complete")
            if text not in nogoods:
                nogoods.append(text)


# runtime.main sends any kind it does not know to python_solver, so replacing it
# keeps main's request parsing, time budget, status and error handling unchanged.
runtime.python_solver = lambda kind, request: essence_solver(request)

if __name__ == "__main__":
    runtime.main("essence")
