import cpmpy as cp


def build(instance):
    total, coins = instance["total_coins_lost"], instance["coin_numbers"]
    bags = cp.intvar(0, total, shape=len(coins), name="bags")
    model = cp.Model(cp.sum([coins[i] * bags[i] for i in range(len(coins))]) == total)
    return model, {"bags": [bags[i] for i in range(len(coins))]}
