import pulp


def build(instance):
    total, coins = instance["total_coins_lost"], instance["coin_numbers"]
    problem = pulp.LpProblem("subset_sum", pulp.LpMinimize)
    bags = [pulp.LpVariable(f"bags_{i}", 0, total, cat="Integer") for i in range(len(coins))]
    problem += pulp.lpSum(coins[i] * bags[i] for i in range(len(coins))) == total
    return problem, {"bags": bags}
