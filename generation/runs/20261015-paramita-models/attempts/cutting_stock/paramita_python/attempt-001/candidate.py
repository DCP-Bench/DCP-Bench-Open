# Cutting stock: choose how many times each cutting pattern is used so that
# every width's orders are met, minimising the number of raw rolls cut.
# Each count x_p is a unary integer (ge[p][i] means x_p >= i + 1), because
# the counts are summed and bounded rather than matched.
from paramita.modelling import Bool, If


def build(instance):
    patterns = instance["num_rolls_width"]  # patterns[p][w] = rolls of width w in pattern p
    orders = instance["orders"]
    num_patterns = instance["num_patterns"]
    num_widths = len(orders)

    # upper bound on the number of rolls of one pattern: the total demand
    # (one roll per piece is always feasible when every width fits)
    ub = max(1, sum(orders))

    ge = [[Bool(f"ge_{p}_{i}") for i in range(ub)] for p in range(num_patterns)]
    cons = []

    # unary order: x_p >= i + 1 implies x_p >= i
    for p in range(num_patterns):
        for i in range(ub - 1):
            cons.append(If(ge[p][i + 1], ge[p][i]))

    # for each width, the total number of rolls cut meets the total Orders
    # (pieces of width w per pattern times the number of rolls of that pattern)
    for w in range(num_widths):
        cons.append(sum(patterns[p][w] * b for p in range(num_patterns) for b in ge[p]) >= orders[w])

    # number of times each pattern is used (x_p = sum of its unary bits)
    counts = [sum(ge[p]) for p in range(num_patterns)]

    # total number of raw rolls cut, to be minimised
    total = sum(counts)

    return cons, {"min_rolls_cut": total, "patterns_used": counts}, ("minimize", total)
