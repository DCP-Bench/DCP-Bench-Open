from ortools.sat.python import cp_model

# The reference's own constants: one row per nutrient, one column per food.
CALORIES = [400, 200, 150, 500]
CHOCOLATE = [3, 2, 0, 0]
SUGAR = [2, 2, 4, 4]
FAT = [2, 4, 1, 5]


def build(instance):
    n, price, limits = instance["n"], instance["price"], instance["limits"]
    model = cp_model.CpModel()
    amount = [model.new_int_var(0, 10000, f"x_{i}") for i in range(n)]
    cost = model.new_int_var(0, 1000, "cost")
    for nutrient, least in zip((CALORIES, CHOCOLATE, SUGAR, FAT), limits):
        model.add(sum(nutrient[i] * amount[i] for i in range(n)) >= least)
    model.add(cost == sum(price[i] * amount[i] for i in range(n)))
    model.minimize(cost)
    return model, {"cost": cost}
