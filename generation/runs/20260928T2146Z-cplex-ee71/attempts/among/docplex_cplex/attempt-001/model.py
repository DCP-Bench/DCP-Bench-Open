"""Among: choose n values in 0..7 such that exactly m of them are among the values of v."""
from docplex.mp.model import Model

# Every x[i] lies in 0..7, as the problem statement fixes.
VALUES = range(8)


def build(instance):
    n, m, v = instance["n"], instance["m"], instance["v"]
    positions = range(n)

    model = Model("among")

    # takes[i, a] is 1 when x[i] equals a; each x[i] takes exactly one value.
    takes = model.binary_var_matrix(positions, VALUES, name="takes")
    for i in positions:
        model.add_constraint(model.sum(takes[i, a] for a in VALUES) == 1, ctname=f"one_value_{i}")

    # Exactly m of the x[i] take a value in v. As in the problem's definition,
    # the count runs over every (i, value of v) pair, so a value listed twice in v
    # counts twice; a value outside 0..7 can never be taken and counts nothing.
    model.add_constraint(model.sum(takes[i, a] for i in positions for a in v if a in VALUES) == m,
                         ctname="among")

    x = [model.sum(a * takes[i, a] for a in VALUES) for i in positions]
    return model, {"x": x}
