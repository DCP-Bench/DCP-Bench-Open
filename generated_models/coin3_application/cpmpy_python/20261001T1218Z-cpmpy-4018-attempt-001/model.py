# Coins: choose how many coins of each denomination to carry, as few as
# possible in total, so that every amount from 1 up to (but not including) the
# maximum can be paid exactly.
import cpmpy as cp


def build(instance):
    denominations = instance["denominations"]   # coin values in cents
    max_amount = instance["max_amount_to_pay"]  # largest amount to pay is max_amount - 1
    n = len(denominations)

    # x[i] = number of coins of denomination i that are carried. No amount below max_amount
    # can use more than max_amount coins of one kind, so max_amount bounds every count.
    x = cp.intvar(0, max_amount, shape=n, name="x")
    # Total number of coins carried, to be minimised.
    num_coins = cp.intvar(0, max_amount, name="num_coins")

    model = cp.Model()

    # The total number of coins is the sum over the denominations.
    model += num_coins == cp.sum(x)

    # Every amount from 1 to max_amount - 1 can be paid with the coins carried: a payment uses
    # no more coins of a kind than are carried, and its coin values add up to the amount.
    for amount in range(1, max_amount):
        used = cp.intvar(0, max_amount, shape=n, name=f"used_{amount}")
        model += cp.sum([denominations[i] * used[i] for i in range(n)]) == amount
        for i in range(n):
            model += used[i] <= x[i]

    # Carry as few coins as possible.
    model.minimize(num_coins)

    return model, {"x": x}
