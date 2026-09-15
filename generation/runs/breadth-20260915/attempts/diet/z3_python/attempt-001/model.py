import z3

# The reference's own constants: one row per nutrient, one column per food.
CALORIES = [400, 200, 150, 500]
CHOCOLATE = [3, 2, 0, 0]
SUGAR = [2, 2, 4, 4]
FAT = [2, 4, 1, 5]


def build(instance):
    n, price, limits = instance["n"], instance["price"], instance["limits"]
    amount = [z3.Int(f"x_{i}") for i in range(n)]
    cost = z3.Int("cost")
    constraints = [a >= 0 for a in amount] + [a <= 10000 for a in amount]
    constraints += [cost >= 0, cost <= 1000]
    for nutrient, least in zip((CALORIES, CHOCOLATE, SUGAR, FAT), limits):
        constraints.append(z3.Sum([nutrient[i] * amount[i] for i in range(n)]) >= least)
    constraints.append(cost == z3.Sum([price[i] * amount[i] for i in range(n)]))
    return constraints, {"cost": cost}, ("minimize", cost)
