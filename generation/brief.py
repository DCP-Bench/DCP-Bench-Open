"""The contract of one problem: declared outputs, objective, instance fields.

Every model starts by extracting the same facts from the reference, and getting
any of them wrong costs an attempt: the declared output *names* come from the
reference's `solution = {...}` dictionary rather than from its variable names,
their shapes have to match exactly, and a model has to read every instance field
it depends on. This prints those facts so they are read rather than inferred.

    python -m generation.brief csplib_056_sonet

It also reports the shape of each instance field, because a ragged or
mixed-type field is what an integration's data interface may be unable to bind
at all; `generation.next_work` uses the same analysis to withhold those pairs.
"""
import argparse
import json
import sys

from evaluation.execution import ROOT
from evaluation.reference import embedded_instance, load_reference
from evaluation.results import EvaluationError

RECTANGULAR_UNIFORM = "rectangular_uniform"


def scalar_type(value):
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    return type(value).__name__


def describe(value):
    """A field's shape, and whether it is ragged or mixes types within a row.

    Both are shapes a data interface may refuse: MiniZinc binds a list of lists
    as a rectangular array of one element type, so either one blocks the pair
    however the model is written.
    """
    if not isinstance(value, list):
        return {"shape": scalar_type(value), "ragged": False, "mixed": False}
    if not value:
        return {"shape": "[]", "ragged": False, "mixed": False}
    parts = [describe(item) for item in value]
    shapes = {part["shape"] for part in parts}
    ragged = any(part["ragged"] for part in parts)
    mixed = any(part["mixed"] for part in parts)
    if len(shapes) > 1:
        # Rows of different lengths are ragged; different scalar types in one
        # row are mixed. Both read as a non-uniform literal to a binder.
        if all(isinstance(item, list) for item in value):
            ragged = True
        else:
            mixed = True
        return {"shape": f"[{len(value)}] of {' | '.join(sorted(shapes))}",
                "ragged": ragged, "mixed": mixed}
    return {"shape": f"[{len(value)}]{parts[0]['shape']}", "ragged": ragged, "mixed": mixed}


def instance_rows(problem):
    path = ROOT / "dataset" / problem / f"{problem}.json"
    try:
        rows = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return []
    return rows if isinstance(rows, list) else []


def fields(problem):
    """Each instance field with its shape, from the first instance available.

    Falls back to the reference's embedded example when no instances are listed,
    and to nothing when neither is readable, so a caller sweeping every problem
    is never stopped by one of them.
    """
    rows = instance_rows(problem)
    instance = rows[0] if rows else None
    if instance is None:
        source = ROOT / "dataset" / problem / f"{problem}.cpmpy.py"
        if not source.is_file():
            return {}
        try:
            instance = embedded_instance(source.read_text(encoding="utf-8"))
        except (OSError, EvaluationError, ValueError, SyntaxError):
            return {}
    return {key: describe(value) for key, value in instance.items()
            if key not in ("name", "note")}


def unbindable(problem):
    """The instance fields that no rectangular, single-type binder can take."""
    return sorted(key for key, shape in fields(problem).items()
                  if shape["ragged"] or shape["mixed"])


def element_type(value):
    """Whether a declared output is Boolean or integer, as the reference built it."""
    return "bool" if getattr(value, "is_bool", lambda: False)() else "int"


def shape_of(value):
    """A declared output's shape, for a CPMpy array, a nested list or a scalar."""
    dimensions = getattr(value, "shape", None)
    if dimensions:
        flat = list(getattr(value, "flat", []))
        inner = element_type(flat[0]) if flat else "int"
        return "".join(f"[{size}]" for size in dimensions) + inner
    if isinstance(value, (list, tuple)):
        inner = {shape_of(item) for item in value}
        return f"[{len(value)}]" + (inner.pop() if len(inner) == 1 else "?")
    return element_type(value)


def brief(problem):
    source = (ROOT / "dataset" / problem / f"{problem}.cpmpy.py").read_text(encoding="utf-8")
    rows = instance_rows(problem)
    instance = rows[0] if rows else embedded_instance(source)
    model, outputs = load_reference(source, instance)
    objective = "satisfaction"
    if model.has_objective():
        objective = "minimize" if getattr(model, "objective_is_min", True) else "maximize"
    return {
        "problem": problem,
        "instances_listed": max(1, len(rows)),
        "objective": objective,
        "declared_outputs": {name: shape_of(value) for name, value in outputs.items()},
        "instance_fields": {key: shape["shape"] for key, shape in fields(problem).items()},
        "unbindable_fields": unbindable(problem),
        "note": "Declared output names come from the reference's solution dictionary, not from "
                "its variable names. Constraints between <SYMMETRY_BREAKING_CONSTRAINT_START> "
                "and _END> markers are commented out in the reference and are not part of the "
                "contract. A field listed under unbindable_fields is ragged or mixes types "
                "within a row, which a rectangular single-type data interface cannot bind.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", help="the problem id, as under dataset/")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(brief(args.problem), indent=2, sort_keys=True))
    except (OSError, EvaluationError, ValueError) as error:
        print(f"generation.brief: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
