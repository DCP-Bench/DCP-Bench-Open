# Production planning: decide how many units x[j] to make of each product j, at most
# u[j] of it, so that the production time used does not exceed b and the total profit
# is as large as possible. Making one unit of product j takes 1/a[j] of the time.
import math

from pychoco.model import Model


def build(instance):
    a = instance["a"]  # a[j]: units of product j made per unit of time
    c = instance["c"]  # c[j]: profit of one unit of product j
    u = instance["u"]  # u[j]: most units of product j that may be made
    b = instance["b"]  # available production time
    n = len(a)

    model = Model()

    # x[j] = units of product j made, between 0 and u[j]
    x = [model.intvar(0, u[j], name=f"x_{j}") for j in range(n)]

    # the time used, sum of x[j] / a[j], is at most b. Choco has integer coefficients only,
    # so both sides are multiplied by the least common multiple of the a[j].
    lcm_a = math.lcm(*a)
    model.scalar(x, [lcm_a // a[j] for j in range(n)], "<=", b * lcm_a).post()

    # total profit (Choco maximises one variable, so it gets its own)
    total_profit = model.intvar(0, sum(c[j] * u[j] for j in range(n)), name="total_profit")
    model.scalar(x, c, "=", total_profit).post()

    return model, {"x": x, "total_profit": total_profit}, ("maximize", total_profit)
