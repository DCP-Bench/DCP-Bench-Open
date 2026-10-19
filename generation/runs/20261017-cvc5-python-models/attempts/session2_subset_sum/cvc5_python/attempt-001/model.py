# Subset sum of coin bags: a bank van had several bags of coins, each bag type
# containing a number of coins from a given list (there are multiple bags of the
# same kind). Some bags were stolen, and a total number of coins was lost. Find
# how many bags were stolen for each type of coin bag.
from cvc5.pythonic import Ints


def build(instance):
    coins = instance["coin_numbers"]
    total = instance["total_coins_lost"]
    k = len(coins)

    bags = Ints(" ".join(f"bags_{i}" for i in range(k)))

    # The number of stolen bags of each type is a non-negative integer.
    # Each type can contribute at most total // coin bags, since every bag holds
    # at least one coin of its type and the lost total is fixed.
    # Bounds are taken from the instance data.
    bounds = []
    for i in range(k):
        bounds.append(bags[i] >= 0)
        bounds.append(bags[i] <= total // coins[i])

    # The stolen bags contain together a given number of coins lost.
    # The bags of each type contribute their coins to the lost total.
    # A given number of coins were lost in total.
    lost = [bags[i] * coins[i] for i in range(k)]
    total_constraint = [sum(lost) == total]

    return bounds + total_constraint, {"bags": list(bags)}
