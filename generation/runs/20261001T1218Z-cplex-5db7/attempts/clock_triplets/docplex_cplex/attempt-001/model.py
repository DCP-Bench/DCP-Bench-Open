"""Clock triplets: rearrange the numbers 1 to 12 on a clock face so that no three adjacent
numbers sum to more than 21.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data. Twelve positions, numbers 1..12, and the bound 21 on
    # every triplet sum are fixed by the problem statement.
    n = 12
    limit = 21
    positions = range(n)
    numbers = range(1, n + 1)

    model = Model("clock_triplets")

    # at[i, v] is 1 when position i shows number v. Every position shows one number and every
    # number appears once (all different).
    at = {(i, v): model.binary_var(name=f"at_{i}_{v}") for i in positions for v in numbers}
    for i in positions:
        model.add_constraint(model.sum(at[i, v] for v in numbers) == 1)
    for v in numbers:
        model.add_constraint(model.sum(at[i, v] for i in positions) == 1)

    # x[i] is the number at position i.
    x = [model.sum(v * at[i, v] for v in numbers) for i in positions]

    # The largest sum of three adjacent numbers, at most 21.
    triplet_sum = model.integer_var(0, limit, name="triplet_sum")

    # Every three adjacent numbers around the circle sum to at most triplet_sum.
    for i in positions:
        model.add_constraint(x[i] + x[i - 1] + x[i - 2] <= triplet_sum)

    return model, {"x": x}
