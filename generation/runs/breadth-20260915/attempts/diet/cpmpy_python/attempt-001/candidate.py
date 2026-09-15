import cpmpy as cp

# The reference's own constants: one row per nutrient, one column per food.
CALORIES = [400, 200, 150, 500]
CHOCOLATE = [3, 2, 0, 0]
SUGAR = [2, 2, 4, 4]
FAT = [2, 4, 1, 5]


def build(instance):
    n, price, limits = instance["n"], instance["price"], instance["limits"]
    amount = cp.intvar(0, 10000, shape=n, name="x")
    cost = cp.intvar(0, 1000, name="cost")
    model = cp.Model()
    for nutrient, least in zip((CALORIES, CHOCOLATE, SUGAR, FAT), limits):
        model += cp.sum([nutrient[i] * amount[i] for i in range(n)]) >= least
    model += cost == cp.sum([price[i] * amount[i] for i in range(n)])
    model.minimize(cost)
    return model, {"cost": cost}
