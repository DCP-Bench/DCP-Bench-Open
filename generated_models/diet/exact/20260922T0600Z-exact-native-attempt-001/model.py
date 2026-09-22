# Cheapest diet meeting every nutritional minimum.
#
# Servings range over 0..10000, which a one-hot encoding could not afford but
# Exact declares as bounds.
from exact import Exact


def build(instance):
    price = instance["price"]
    limits = instance["limits"]
    n = instance["n"]

    # The macro table belongs to the problem statement, not to the instance:
    # calories, chocolate, sugar and fat per serving of each of the four foods.
    macros = [
        [400, 200, 150, 500],
        [3, 2, 0, 0],
        [2, 2, 4, 4],
        [2, 4, 1, 5],
    ]

    solver = Exact()
    # 0..10000 servings and 0..1000 cents are the bounds the reference declares.
    x = [f"x{j}" for j in range(n)]
    for name in x:
        solver.addVariable(name, 0, 10000)
    for row, least in zip(macros, limits):
        solver.addConstraint([(row[j], x[j]) for j in range(n) if row[j]],
                             True, least)

    solver.addVariable("cost", 0, 1000)
    solver.addConstraint(list(zip(price, x)) + [(-1, "cost")], True, 0, True, 0)
    return solver, {"cost": "cost"}, ("minimize", [(1, "cost")])
