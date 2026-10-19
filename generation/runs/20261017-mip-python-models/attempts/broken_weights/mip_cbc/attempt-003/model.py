# Broken weights: a measuring weight of m pounds broke into n pieces, each a whole
# number of pounds. The pieces must be usable to weigh every whole number of pounds
# from 1 to m, with pieces placed on the object's pan, on the other pan, or off the scale.
import mip


def build(instance):
    total = instance["m"]
    n = instance["n"]
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    # every piece is at least 1 pound, so no piece is heavier than total - (n - 1)
    top = total - (n - 1)
    values = range(1, top + 1)

    # one-hot choice of the weight of each piece
    x = [
        {v: model.add_var(f"x_{i}_{v}", var_type=mip.BINARY) for v in values}
        for i in range(n)
    ]
    weights = []
    for i in range(n):
        # each piece has exactly one whole-pound weight
        model.add_constr(mip.xsum(x[i][v] for v in values) == 1)
        w = model.add_var(f"w_{i}", lb=1, ub=top, var_type=mip.INTEGER)
        model.add_constr(w == mip.xsum(v * x[i][v] for v in values))
        weights.append(w)

    # the pieces together weigh the original measure
    model.add_constr(mip.xsum(weights) == total)

    # count[v]: number of pieces of weight v; used[v]: 1 if some piece has weight v
    count = {}
    used = {}
    for v in values:
        count[v] = mip.xsum(x[i][v] for i in range(n))
        used[v] = model.add_var(f"used_{v}", var_type=mip.BINARY)
        model.add_constr(count[v] <= n * used[v])

    # the pieces can be used to weigh every integral weight between 1 and the total weight.
    # Pieces weighing less than v, with a value v in use, can weigh every amount up to
    # their own total S. A piece of weight v extends that range to S + v exactly when
    # v <= 2 * S + 1. So every used weight v must satisfy v <= 2 * S(v) + 1, where S(v)
    # is the total weight of the pieces strictly lighter than v.
    for v in values:
        lighter = mip.xsum(u * count[u] for u in values if u < v)
        model.add_constr(v * used[v] <= 2 * lighter + 1)

    return model, {"weights": weights}
