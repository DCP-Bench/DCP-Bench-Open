import pulp


def build(instance):
    """Birthday coins: fifteen old British coins worth one pound five and six.
    Working in pence: a half-crown is 30, a shilling 12, a sixpence 6.
    """
    del instance

    values = [30, 12, 6]
    problem = pulp.LpProblem("coins", pulp.LpMinimize)
    coins = [pulp.LpVariable(f"c{i}", 0, 15, cat="Integer") for i in range(3)]

    problem += pulp.lpSum(values[i] * coins[i] for i in range(3)) == 306
    problem += pulp.lpSum(coins) == 15

    return problem, {"half_crowns": coins[0]}
