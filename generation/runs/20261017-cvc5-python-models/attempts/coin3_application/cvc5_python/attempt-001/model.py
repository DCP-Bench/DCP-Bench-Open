# coin3_application: find the minimum number of coins that allows one to pay exactly
# any amount smaller than a given maximum amount, using a given set of denominations.
# Output x[k] is the number of coins of denomination k.

import cvc5.pythonic as cz


def build(instance):
    den = instance["denominations"]
    top = instance["max_amount_to_pay"]
    nd = len(den)

    x = [cz.Int(f"x_{k}") for k in range(nd)]
    constraints = []

    # Number of coins of each denomination: no more than needed to pay any amount below the maximum.
    for k in range(nd):
        constraints.append(x[k] >= 0)
        constraints.append(x[k] <= (top - 1) // den[k])

    # Pay exactly any amount smaller than the maximum amount, using at most the coins available.
    for amount in range(1, top):
        y = [cz.Int(f"y_{amount}_{k}") for k in range(nd)]
        for k in range(nd):
            constraints.append(y[k] >= 0)
            constraints.append(y[k] <= amount // den[k])
            constraints.append(y[k] <= x[k])
        constraints.append(cz.Sum([den[k] * y[k] for k in range(nd)]) == amount)

    # Minimize the total number of coins.
    total = cz.Sum(x)

    return constraints, {"x": x}, ("minimize", total)
