"""Bank van coin bags: how many bags of each type were stolen so that the coins lost add up to the total.

Bag type i holds coin_numbers[i] coins. The count of stolen bags of each type is
one-hot encoded over 0..total_coins_lost // coin_numbers[i], since more bags than that
could not add up to the total.
"""
from paramita.modelling import Bool


def build(instance):
    coins = instance["coin_numbers"]
    total = instance["total_coins_lost"]

    # one-hot count of stolen bags per bag type: counts[i][k] is true when k bags of type i were stolen
    counts = []
    for i, c in enumerate(coins):
        ub = total // c
        counts.append({k: Bool(f"bags_{i}_{k}") for k in range(ub + 1)})

    cons = []
    # each bag type has exactly one stolen-bag count
    for i in range(len(coins)):
        cons.append(sum(counts[i].values()) == 1)

    # the stolen bags hold the total number of coins lost
    lost = sum(c * k * counts[i][k] for i, c in enumerate(coins) for k in range(1, len(counts[i])))
    cons.append(lost == total)

    # number of bags stolen of each type
    bags = [sum(k * counts[i][k] for k in range(1, len(counts[i]))) for i in range(len(coins))]
    return cons, {"bags": bags}
