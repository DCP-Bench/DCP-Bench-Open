# Money change: give back an amount of money using the available coins of several
# types, with as few coins as possible.
from pychoco.model import Model


def build(instance):
    amount = instance["amount"]  # amount of money to give
    types_of_coins = instance["types_of_coins"]  # value of each type of coin
    available_coins = instance["available_coins"]  # number of coins available of each type
    n = len(types_of_coins)

    model = Model()

    # coin_counts[i] = number of coins of type i given; no more than are available
    coin_counts = [model.intvar(0, available_coins[i], name=f"coin_counts_{i}") for i in range(n)]

    # the values of the coins given add up to the amount
    model.scalar(coin_counts, types_of_coins, "=", amount).post()

    # total number of coins given (Choco minimises one variable, so it gets its own)
    total_coins = model.intvar(0, sum(available_coins), name="total_coins")
    model.sum(coin_counts, "=", total_coins).post()

    return model, {"coin_counts": coin_counts}, ("minimize", total_coins)
