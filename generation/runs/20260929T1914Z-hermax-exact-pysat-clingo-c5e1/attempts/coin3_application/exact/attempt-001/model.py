# Coins: choose how many coins of each denomination to carry, as few as
# possible in total, so that every amount from 1 up to (but not including) the
# maximum can be paid exactly.
from exact import Exact


def build(instance):
    denominations = instance["denominations"]  # coin values in cents
    max_amount = instance["max_amount_to_pay"]  # largest amount is max_amount - 1
    n = len(denominations)

    solver = Exact()
    # x[i] = number of coins of denomination i that are carried
    x = [f"x_{i}" for i in range(n)]
    for name in x:
        solver.addVariable(name, 0, max_amount)

    # every amount from 1 to max_amount - 1 can be paid with the coins carried:
    # a payment uses no more coins of a kind than are carried and adds up to the amount
    for amount in range(1, max_amount):
        used = [f"used_{amount}_{i}" for i in range(n)]
        for i in range(n):
            solver.addVariable(used[i], 0, max_amount)
            solver.addConstraint([(1, x[i]), (-1, used[i])], True, 0)
        solver.addConstraint([(denominations[i], used[i]) for i in range(n)], True, amount, True, amount)

    # carry as few coins as possible
    return solver, {"x": x}, ("minimize", [(1, name) for name in x])
