# Coins: choose how many coins of each denomination to carry, as few as
# possible in total, so that every amount from 1 up to (but not including) the
# maximum can be paid exactly.
from pychoco.model import Model


def build(instance):
    denominations = instance["denominations"]  # coin values in cents
    max_amount = instance["max_amount_to_pay"]  # largest amount is max_amount - 1
    n = len(denominations)

    model = Model()

    # x[i] = number of coins of denomination i that are carried
    x = [model.intvar(0, max_amount, name=f"x_{i}") for i in range(n)]

    # every amount from 1 to max_amount - 1 can be paid with the coins carried:
    # a payment uses no more coins of a kind than are carried and adds up to the amount
    for amount in range(1, max_amount):
        used = [model.intvar(0, max_amount, name=f"used_{amount}_{i}") for i in range(n)]
        for i in range(n):
            model.arithm(used[i], "<=", x[i]).post()
        model.scalar(used, denominations, "=", amount).post()

    # carry as few coins as possible (Choco minimises one variable, so the total is tied to it)
    num_coins = model.intvar(0, max_amount, name="num_coins")
    model.sum(x, "=", num_coins).post()

    return model, {"x": x}, ("minimize", num_coins)
