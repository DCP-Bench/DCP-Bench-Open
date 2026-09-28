"""Diet: buy whole units of four foods so that every nutritional minimum is met at the least cost."""
import gurobipy as gp
from gurobipy import GRB

# Nutrients per unit of each food (cake, ice cream, cola, cheesecake). This table
# belongs to the problem statement, not to an instance, so it is mirrored here.
CALORIES = [400, 200, 150, 500]
CHOCOLATE = [3, 2, 0, 0]
SUGAR = [2, 2, 4, 4]
FAT = [2, 4, 1, 5]


def build(instance):
    price = instance["price"]
    limits = instance["limits"]  # minimum calories, chocolate, sugar and fat
    foods = range(instance["n"])

    model = gp.Model("diet")

    # x[f] is how many units of food f are bought; the bound of 10000 is the
    # domain the problem's reference model declares.
    x = model.addVars(foods, lb=0, ub=10000, vtype=GRB.INTEGER, name="x")

    # Each nutrient reaches its minimum.
    for name, per_unit, minimum in zip(("calories", "chocolate", "sugar", "fat"),
                                       (CALORIES, CHOCOLATE, SUGAR, FAT), limits):
        model.addConstr(gp.quicksum(per_unit[f] * x[f] for f in foods) >= minimum, name=name)

    # cost is the price of the diet; the reference model bounds it to 0..1000.
    # It is a variable of its own, not just the objective expression, so that the
    # declared output is this one integer rather than every quantity behind it.
    cost = model.addVar(lb=0, ub=1000, vtype=GRB.INTEGER, name="cost")
    model.addConstr(cost == gp.quicksum(price[f] * x[f] for f in foods), name="price")

    # Minimise the cost.
    model.setObjective(cost, GRB.MINIMIZE)

    return model, {"cost": cost}
