# Diet: choose how many units of each food to buy so that every nutritional
# requirement is met at the lowest total cost in cents.
from pychoco.model import Model

# Nutrition table of the four foods (chocolate cake, chocolate ice cream, cola,
# pineapple cheesecake). It is fixed by the problem statement, not by the instance;
# the instance supplies the prices and the minimum amounts required.
CALORIES = [400, 200, 150, 500]
CHOCOLATE = [3, 2, 0, 0]
SUGAR = [2, 2, 4, 4]
FAT = [2, 4, 1, 5]


def build(instance):
    n = instance["n"]  # number of foods
    price = instance["price"]  # price of one unit of each food, in cents
    limits = instance["limits"]  # required amount of calories, chocolate, sugar, fat (at least)

    model = Model()

    # x[i] = number of units of food i that are bought (upper bound as in the problem statement)
    x = [model.intvar(0, 10000, name=f"x_{i}") for i in range(n)]

    # every nutrition type must reach its required amount
    for amounts, required in zip((CALORIES, CHOCOLATE, SUGAR, FAT), limits):
        model.scalar(x, amounts[:n], ">=", required).post()

    # total cost of the diet, the quantity to minimise (upper bound as in the problem statement)
    cost = model.intvar(0, 1000, name="cost")
    model.scalar(x, price, "=", cost).post()

    return model, {"cost": cost}, ("minimize", cost)
