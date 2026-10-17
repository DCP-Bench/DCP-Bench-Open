# Diet problem: given the prices of the foods and the nutritional requirements (at least)
# for each nutrition type, find the diet of minimal cost.
import cvc5.pythonic as cz

# Nutrient content per unit of each food, from the problem description.
# Columns: calories, chocolate (ounces), sugar (ounces), fat (ounces).
NUTRIENTS = [
    [400, 3, 2, 2],  # Chocolate Cake (1 slice)
    [200, 2, 2, 4],  # Chocolate ice cream (1 scoop)
    [150, 0, 4, 1],  # Cola (1 bottle)
    [500, 0, 4, 5],  # Pineapple cheesecake (1 piece)
]


def build(instance):
    n = instance["n"]
    price = instance["price"]
    limits = instance["limits"]

    # Number of units of each food in the diet.
    x = [cz.Int(f"x_{i}") for i in range(n)]

    constraints = []

    # The number of units bought is a non-negative whole number.
    # (cvc5 integers are unbounded, so this bound is required.)
    # Quantities of each food cannot be negative.
    for i in range(n):
        constraints.append(x[i] >= 0)

    # The diet must provide at least the required amount of each nutrition type:
    # calories, chocolate, sugar and fat.
    for j in range(len(limits)):
        constraints.append(
            cz.Sum([NUTRIENTS[i][j] * x[i] for i in range(n)]) >= limits[j]
        )

    # The optimal diet minimises the cost of the products.
    cost = cz.Sum([price[i] * x[i] for i in range(n)])

    return constraints, {"cost": cost}, ("minimize", cost)
