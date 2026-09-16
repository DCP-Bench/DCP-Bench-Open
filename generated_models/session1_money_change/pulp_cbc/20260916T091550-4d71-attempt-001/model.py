import pulp


def build(instance):
    """Money change: make the amount exactly from the coins on hand, using as
    few coins as possible.
    """
    amount = instance["amount"]
    types_of_coins = instance["types_of_coins"]
    available_coins = instance["available_coins"]
    n = len(types_of_coins)
    max_available = max(available_coins)

    problem = pulp.LpProblem("change", pulp.LpMinimize)
    counts = [pulp.LpVariable(f"c{i}", 0, max_available, cat="Integer")
              for i in range(n)]

    problem += pulp.lpSum(types_of_coins[i] * counts[i] for i in range(n)) == amount
    for i in range(n):
        problem += counts[i] <= available_coins[i]

    problem += pulp.lpSum(counts)

    return problem, {"coin_counts": counts}
