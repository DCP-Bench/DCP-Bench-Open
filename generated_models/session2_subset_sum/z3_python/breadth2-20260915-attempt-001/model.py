import z3


def build(instance):
    total, coins = instance["total_coins_lost"], instance["coin_numbers"]
    bags = [z3.Int(f"bags_{i}") for i in range(len(coins))]
    constraints = [b >= 0 for b in bags] + [b <= total for b in bags]
    constraints.append(z3.Sum([coins[i] * bags[i] for i in range(len(coins))]) == total)
    return constraints, {"bags": bags}
