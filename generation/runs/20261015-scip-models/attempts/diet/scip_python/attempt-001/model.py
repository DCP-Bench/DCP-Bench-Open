# Diet: choose whole numbers of four foods that meet the minimum amount of each
# nutrient at the lowest total cost.
from pyscipopt import Model, quicksum

# Nutrient content of one item of each food, from the problem's table. Columns are
# calories, chocolate (ounces), sugar (ounces), fat (ounces). This is a fixed fact of
# the problem, not part of the instance.
NUTRIENTS = [
    [400, 3, 2, 2],  # Chocolate Cake (1 slice)
    [200, 2, 2, 4],  # Chocolate ice cream (1 scoop)
    [150, 0, 4, 1],  # Cola (1 bottle)
    [500, 0, 4, 5],  # Pineapple cheesecake (1 piece)
]
NUTRIENT_NAMES = ["calories", "chocolate", "sugar", "fat"]


def build(instance):
    n = instance["n"]
    price = instance["price"]
    limits = instance["limits"]

    m = Model()

    # buy[j] = number of items of food j, a whole number
    # The bound is the largest count that could be needed to meet one nutrient alone.
    # Prices are not negative, so buying more than this never lowers the optimal cost.
    buy = []
    for j in range(n):
        ub = max(
            -(-limits[i] // NUTRIENTS[j][i])  # ceiling division
            for i in range(len(limits))
            if NUTRIENTS[j][i] > 0
        )
        buy.append(m.addVar(name=f"buy_{j}", vtype="I", lb=0, ub=ub))

    # the diet must provide at least the required amount of each nutrient
    for i in range(len(limits)):
        m.addCons(
            quicksum(NUTRIENTS[j][i] * buy[j] for j in range(n)) >= limits[i],
            name=f"min_{NUTRIENT_NAMES[i]}",
        )

    # the cost of the diet is the price of every item bought
    cost = quicksum(price[j] * buy[j] for j in range(n))
    m.setObjective(cost, "minimize")

    return m, {"cost": cost}
