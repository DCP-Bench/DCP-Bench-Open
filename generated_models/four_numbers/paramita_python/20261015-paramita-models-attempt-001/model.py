# Four numbers: find three integers x1, x2, x3 between 1 and 10 such that every
# input number is the sum of some non-empty subset of x1, x2, x3.
# Each x_i is one-hot over the values 1..10 (integer value = sum of v * bit).
from itertools import combinations
from paramita.modelling import Bool, Or, If

DOMAIN = range(1, 11)


def build(instance):
    numbers = instance["numbers"]
    cons = []

    # the three integers are each between 1 and 10 inclusive
    xv = [{v: Bool(f"x_{i}_{v}") for v in DOMAIN} for i in range(3)]
    cons += [sum(xv[i].values()) == 1 for i in range(3)]
    x = [sum(v * xv[i][v] for v in DOMAIN) for i in range(3)]

    # the non-empty subsets of the three integers
    subsets = [S for r in (1, 2, 3) for S in combinations(range(3), r)]

    # each input number is the sum of some subset of the three integers
    for n_idx, n in enumerate(numbers):
        sel = {S: Bool(f"s_{n_idx}_{''.join(map(str, S))}") for S in subsets}
        cons.append(Or(list(sel.values())))
        for S, b in sel.items():
            # if this subset is the one used, its sum is the input number
            cons.append(If(b, sum(x[i] for i in S) == n))

    return cons, {"x": x}
