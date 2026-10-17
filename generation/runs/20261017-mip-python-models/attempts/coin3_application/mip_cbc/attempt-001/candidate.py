# Coin problem (coin3_application): find the minimum number of coins of each
# denomination such that every amount smaller than the maximum amount can be
# paid exactly with the coins chosen. Output x gives the number of each coin.
import mip


def build(instance):
    d = instance["denominations"]
    max_amount = instance["max_amount_to_pay"]
    n = len(d)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Number of coins of each denomination. Using more than floor((max-1)/d_i)
    # coins of type i is never needed to pay any amount below max, so this
    # bound keeps every optimal solution.
    x = [
        model.add_var(f"x_{i}", lb=0, ub=(max_amount - 1) // d[i], var_type=mip.INTEGER)
        for i in range(n)
    ]

    # Every amount a with 1 <= a < max must be paid exactly with coins that are
    # available: the coins y used for a are at most the coins x available.
    for a in range(1, max_amount):
        y = [
            model.add_var(f"y_{a}_{i}", lb=0, ub=a // d[i], var_type=mip.INTEGER)
            for i in range(n)
        ]
        # the payment for amount a
        model += mip.xsum(d[i] * y[i] for i in range(n)) == a
        # only available coins can be used
        for i in range(n):
            model += y[i] <= x[i]

    # the total number of coins, to minimise
    model.objective = mip.xsum(x)

    return model, {"x": x}
