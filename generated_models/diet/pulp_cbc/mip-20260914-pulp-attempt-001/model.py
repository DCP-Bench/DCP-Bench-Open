import pulp

# The reference's own constants: one row per nutrient, one column per food.
CALORIES = [400, 200, 150, 500]
CHOCOLATE = [3, 2, 0, 0]
SUGAR = [2, 2, 4, 4]
FAT = [2, 4, 1, 5]


def build(instance):
    n, price, limits = instance["n"], instance["price"], instance["limits"]
    problem = pulp.LpProblem("diet", pulp.LpMinimize)
    amount = [pulp.LpVariable(f"x_{i}", 0, 10000, cat="Integer") for i in range(n)]
    cost = pulp.LpVariable("cost", 0, 1000, cat="Integer")
    for nutrient, least in zip((CALORIES, CHOCOLATE, SUGAR, FAT), limits):
        problem += pulp.lpSum(nutrient[i] * amount[i] for i in range(n)) >= least
    problem += cost == pulp.lpSum(price[i] * amount[i] for i in range(n))
    problem += cost
    return problem, {"cost": cost}
