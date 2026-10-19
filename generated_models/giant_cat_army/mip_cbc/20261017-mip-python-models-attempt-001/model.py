# Giant cat army: build a list x of 24 distinct integers, each between 0 and 60, starting
# with 0 and ending with 14. Each step adds 5, adds 7, or takes the square root of a perfect
# square. The list contains 2, 10 and 14 in that order; other numbers may sit between them.
import mip

LENGTH = 24
MAX_VALUE = 60
ROOTS = range(1, 8)  # roots of the perfect squares 1..49; 0 is left out (it would repeat the start)


def _equal_when(model, expr, rhs, bigm, switch):
    # expr == rhs whenever switch == 1; bigm bounds |expr - rhs| from the data
    model.add_constr(expr - rhs <= bigm * (1 - switch))
    model.add_constr(expr - rhs >= -bigm * (1 - switch))


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    values = range(MAX_VALUE + 1)
    x = [model.add_var(f"x_{i}", lb=0, ub=MAX_VALUE, var_type=mip.INTEGER) for i in range(LENGTH)]
    # one-hot value of each position, so that distinctness and the presence of 2, 10, 14 are linear
    p = [[model.add_var(f"p_{i}_{v}", var_type=mip.BINARY) for v in values] for i in range(LENGTH)]

    # the list has 24 integers, each at most 60, and all elements are distinct
    for i in range(LENGTH):
        model.add_constr(mip.xsum(p[i]) == 1)
        model.add_constr(x[i] == mip.xsum(v * p[i][v] for v in values))
    for v in values:
        model.add_constr(mip.xsum(p[i][v] for i in range(LENGTH)) <= 1)

    # starting with [0]
    model.add_constr(x[0] == 0)
    # ending with 14
    model.add_constr(x[LENGTH - 1] == 14)

    # each step adds 5, adds 7, or takes the square root of a perfect square
    add5 = [model.add_var(f"add5_{i}", var_type=mip.BINARY) for i in range(LENGTH - 1)]
    add7 = [model.add_var(f"add7_{i}", var_type=mip.BINARY) for i in range(LENGTH - 1)]
    root = [
        {r: model.add_var(f"root_{i}_{r}", var_type=mip.BINARY) for r in ROOTS}
        for i in range(LENGTH - 1)
    ]
    for i in range(LENGTH - 1):
        model.add_constr(add5[i] + add7[i] + mip.xsum(root[i].values()) == 1)

    # adding 5: the next number is the current number plus 5
    # adding 7: the next number is the current number plus 7
    for i in range(LENGTH - 1):
        _equal_when(model, x[i + 1] - x[i], 5, MAX_VALUE + 5, add5[i])
        _equal_when(model, x[i + 1] - x[i], 7, MAX_VALUE + 7, add7[i])

    # taking the square root: the current number is r*r and the next number is r
    for i in range(LENGTH - 1):
        sq = mip.xsum(root[i].values())
        _equal_when(model, x[i] - mip.xsum(r * r * root[i][r] for r in ROOTS), 0, MAX_VALUE, sq)
        _equal_when(model, x[i + 1] - mip.xsum(r * root[i][r] for r in ROOTS), 0, MAX_VALUE, sq)

    # the list contains 2, 10 and 14 in that order, other numbers may sit between them
    def pos(v):
        return mip.xsum(i * p[i][v] for i in range(LENGTH))

    for v in (2, 10, 14):
        model.add_constr(mip.xsum(p[i][v] for i in range(LENGTH)) == 1)
    model.add_constr(pos(2) + 1 <= pos(10))
    model.add_constr(pos(10) + 1 <= pos(14))

    # satisfaction problem: no objective
    return model, {"x": x}
