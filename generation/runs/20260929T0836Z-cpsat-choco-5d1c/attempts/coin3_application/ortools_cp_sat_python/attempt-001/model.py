# Coins: choose how many coins of each denomination to carry, as few as
# possible in total, so that every amount from 1 up to (but not including) the
# maximum can be paid exactly.
from ortools.sat.python import cp_model


def build(instance):
    denominations = instance["denominations"]  # coin values in cents
    max_amount = instance["max_amount_to_pay"]  # largest amount is max_amount - 1
    n = len(denominations)

    model = cp_model.CpModel()

    # x[i] = number of coins of denomination i that are carried
    x = [model.new_int_var(0, max_amount, f"x_{i}") for i in range(n)]

    # every amount from 1 to max_amount - 1 can be paid with the coins carried:
    # a payment uses no more coins of a kind than are carried and adds up to the amount
    for amount in range(1, max_amount):
        used = [model.new_int_var(0, max_amount, f"used_{amount}_{i}") for i in range(n)]
        for i in range(n):
            model.add(used[i] <= x[i])
        model.add(sum(denominations[i] * used[i] for i in range(n)) == amount)

    # carry as few coins as possible
    num_coins = model.new_int_var(0, max_amount, "num_coins")
    model.add(num_coins == sum(x))
    model.minimize(num_coins)

    return model, {"x": x}
