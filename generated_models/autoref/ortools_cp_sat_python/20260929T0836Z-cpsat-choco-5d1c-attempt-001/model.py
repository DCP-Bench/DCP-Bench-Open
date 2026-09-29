# Autoref: find a series s[0..n+1] in which every i from 0 to n occurs exactly
# s[i] times, and whose last element s[n+1] equals m.
from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]
    m = instance["m"]  # required value of the last element

    model = cp_model.CpModel()

    # the series has n + 2 positions; every value lies between 0 and n
    s = [model.new_int_var(0, n, f"s_{k}") for k in range(n + 2)]

    # the last element is m
    model.add(s[n + 1] == m)

    # the value i occurs exactly s[i] times in the series. CP-SAT has no
    # counting constraint, so each position gets one Boolean per value that is
    # true exactly when the position holds that value, and the Booleans of a
    # value are summed.
    for i in range(n + 1):
        holds = []
        for k in range(n + 2):
            b = model.new_bool_var(f"is_{k}_{i}")
            model.add(s[k] == i).only_enforce_if(b)
            model.add(s[k] != i).only_enforce_if(b.negated())
            holds.append(b)
        model.add(sum(holds) == s[i])

    return model, {"s": s}
