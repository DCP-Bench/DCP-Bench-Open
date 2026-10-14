"""MiniZinc on Gecode, with the instance binding this integration adds.

MiniZinc's data interface takes only rectangular arrays whose elements share one
type: it mixes Booleans, integers and floats, but not strings with numbers, and
not scalars with arrays. A dataset field outside that shape would fail before
any model runs, so each JSON instance field is bound by these rules. Every array
is indexed from 1, as MiniZinc indexes a JSON array.

1. A field MiniZinc accepts binds unchanged. When it is a nonempty list of
   lists, `<field>_len` (each row's length) is bound beside it, so a model that
   needs the row lengths of a field that is ragged in other instances runs on
   this one too. It is left out when an instance field already has that name.
2. A ragged list of rows, whose items all have one shape and whose scalars all
   have one type, binds as `<field>`, padded to the longest row with 0, false,
   0.0 or "" in every padded position, plus `<field>_len`. The items may be
   scalars (a 2-D array) or equal-shape arrays (one more dimension each).
3. A list of equal-length rows whose columns have different types (strings
   beside numbers, or scalars beside arrays) binds as one array per column,
   `<field>_1`, `<field>_2`, ..., numbered from 1; `<field>` itself is not
   bound. Each column then binds by rule 1 or rule 2, but is not split again.
4. Any other ragged or mixed field is refused, as is a generated name that is
   already an instance field or is generated twice.

A refusal is an `error` status with the reason as detail, exactly as any other
failure in `runtime.main`, because the binding runs inside it.
"""
import sys
sys.path.insert(0, "/opt/runner")
import runtime


class Unbindable(ValueError):
    pass


def kind(value):
    if isinstance(value, str):
        return "string"
    if isinstance(value, (bool, int, float)):
        return "number"
    return "other"


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


def pad_value(scalars):
    if scalars and all(isinstance(x, str) for x in scalars):
        return ""
    if scalars and all(isinstance(x, bool) for x in scalars):
        return False
    if any(isinstance(x, float) for x in scalars):
        return 0.0
    return 0


def filled(dimensions, value):
    if not dimensions:
        return value
    return [filled(dimensions[1:], value) for _ in range(dimensions[0])]


def column_class(column):
    """"array", "string" or "number" when the column is one of them, else None."""
    if all(isinstance(item, list) for item in column):
        return "array"
    kinds = {kind(item) for item in column}  # a list among scalars reads as "other"
    return kinds.pop() if len(kinds) == 1 and "other" not in kinds else None


def field(name, value, split=True):
    """Yield (name, value, required) bindings for one instance field."""
    if not isinstance(value, list) or "other" in {kind(x) for x in leaves(value)}:
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
            pad = filled(shapes[0][0], pad_value(leaves(items)))
            yield name, [row + [pad] * (longest - len(row)) for row in value], True
            yield f"{name}_len", [len(row) for row in value], True
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


def bind(instance):
    required, optional = {}, {}
    for name, value in instance.items():
        for key, data, needed in field(name, value):
            if not needed:
                optional[key] = data
                continue
            if key in required or (key != name and key in instance):
                raise Unbindable(f"Instance field `{name}` binds as `{key}`, which is already "
                                 "an instance field or another generated name")
            required[key] = data
    for key, data in optional.items():
        if key not in instance and key not in required:
            required[key] = data
    return required


solve = runtime.minizinc_solver


def minizinc_solver(request):
    if not request["legacy"]:
        request = {**request, "instance": bind(request["instance"])}
    return solve(request)


# runtime.main dispatches to the module-level minizinc_solver, so replacing it
# keeps main's request parsing, time budget, status and error handling unchanged.
runtime.minizinc_solver = minizinc_solver

if __name__ == "__main__":
    runtime.main("minizinc")
