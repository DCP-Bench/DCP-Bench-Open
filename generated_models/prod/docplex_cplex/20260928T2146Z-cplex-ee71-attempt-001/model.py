"""Production planning: choose production quantities within their limits and the time budget to maximise profit."""
import math

from docplex.mp.model import Model


def build(instance):
    a, c, u = instance["a"], instance["c"], instance["u"]
    products = range(len(a))

    model = Model("prod")

    # x[j] is the quantity of product j, between 0 and u[j].
    x = [model.integer_var(0, u[j], name=f"x_{j}") for j in products]

    # Producing x[j] takes x[j] / a[j] of the budget b. Scaling both sides by the
    # least common multiple of the a[j] keeps every coefficient an integer, so the
    # check is exact rather than subject to floating-point tolerance.
    lcm_a = math.lcm(*a)
    model.add_constraint(model.sum((lcm_a // a[j]) * x[j] for j in products) <= instance["b"] * lcm_a,
                         ctname="budget")

    # Maximise the total profit.
    total_profit = model.dot(x, c)
    model.maximize(total_profit)

    return model, {"x": x, "total_profit": total_profit}
