# Pythagorean triplet with a + b + c = 1000: natural numbers a < b < c with
# a^2 + b^2 = c^2 and a + b + c = 1000. Report a, b and c.
import mip

N = 1000  # the sum fixed by the description


def one_hot(model, name, lo, hi):
    # integer variable x in lo..hi, linked to one binary per value
    picks = {v: model.add_var(f"{name}_is_{v}", var_type=mip.BINARY) for v in range(lo, hi + 1)}
    x = model.add_var(name, lb=lo, ub=hi, var_type=mip.INTEGER)
    model.add_constr(mip.xsum(picks.values()) == 1)
    model.add_constr(x == mip.xsum(v * p for v, p in picks.items()))
    return x, picks


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    model.verbose = 0
    model.max_mip_gap = 0.0
    model.max_mip_gap_abs = 0.0

    # Bounds follow from a >= 1, a < b < c and a + b + c = N.
    a_max = (N - 3) // 3
    b_max = (N - 2) // 2
    c_max = N - 3

    # The three numbers are natural numbers with a < b < c.
    a, a_pick = one_hot(model, "a", 1, a_max)
    b, b_pick = one_hot(model, "b", 2, b_max)
    c, c_pick = one_hot(model, "c", 3, c_max)

    # a < b < c
    model.add_constr(a + 1 <= b)
    model.add_constr(b + 1 <= c)

    # a + b + c = 1000
    model.add_constr(a + b + c == N)

    # a^2 + b^2 = c^2, with the squares read from the one-hot values
    square_a = mip.xsum(v * v * p for v, p in a_pick.items())
    square_b = mip.xsum(v * v * p for v, p in b_pick.items())
    square_c = mip.xsum(v * v * p for v, p in c_pick.items())
    model.add_constr(square_a + square_b == square_c)

    return model, {"a": a, "b": b, "c": c}
