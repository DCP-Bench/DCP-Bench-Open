# Problem session5_hardy_1729_square: find 4 different numbers between 1 and 100
# such that a^2 + b^2 = c^2 + d^2; output (a, b, c, d).
import mip


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    names = ["a", "b", "c", "d"]
    values = list(range(1, 101))

    # Each number is an integer in 1..100 with a one-hot encoding over its values,
    # so that its square becomes linear in the one-hot binaries.
    x = {n: model.add_var(n, lb=1, ub=100, var_type=mip.INTEGER) for n in names}
    p = {
        n: {v: model.add_var(f"p_{n}_{v}", var_type=mip.BINARY) for v in values}
        for n in names
    }
    for n in names:
        # each number takes exactly one value
        model += mip.xsum(p[n][v] for v in values) == 1
        model.add_constr(x[n] == mip.xsum(v * p[n][v] for v in values))

    # The four numbers are different: each value is used by at most one of them.
    for v in values:
        model += mip.xsum(p[n][v] for n in names) <= 1

    # a^2 + b^2 = c^2 + d^2
    sq_ab = mip.xsum([v * v * p["a"][v] for v in values] + [v * v * p["b"][v] for v in values])
    sq_cd = mip.xsum([v * v * p["c"][v] for v in values] + [v * v * p["d"][v] for v in values])
    model += sq_ab == sq_cd

    # Satisfaction problem: no objective.
    return model, {"a": x["a"], "b": x["b"], "c": x["c"], "d": x["d"]}
