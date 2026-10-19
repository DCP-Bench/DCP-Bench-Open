# Production planning (prod): choose an integer production quantity X[j] for each
# product j to maximize the total profit, the sum of c[j] * X[j].
# The description's resource row is sum((1/a[j]) * X[j]) <= b. It is scaled by
# L = lcm(a) so that every coefficient is the integer L // a[j] and the right-hand
# side is L * b, which keeps the row exact in CBC.
import math

import mip


def build(instance):
    a = instance["a"]
    b = instance["b"]
    c = instance["c"]
    u = instance["u"]
    n = len(a)

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # The production quantities: integers between 0 and u[j].
    X = [model.add_var(f"X_{j}", lb=0, ub=u[j], var_type=mip.INTEGER) for j in range(n)]

    # The total profit is an integer tied to the sum of c[j] * X[j] by an equality row.
    profit_lo = sum(min(0, c[j] * u[j]) for j in range(n))
    profit_hi = sum(max(0, c[j] * u[j]) for j in range(n))
    total = model.add_var("total_profit", lb=profit_lo, ub=profit_hi, var_type=mip.INTEGER)

    # The sum of (1/a[j]) * X[j] over all products should be less than or equal to b.
    L = math.lcm(*a)
    model.add_constr(
        mip.xsum((L // a[j]) * X[j] for j in range(n)) <= L * b,
        name="resource",
    )

    # The total profit is the sum of c[j] * X[j] over all products.
    model.add_constr(
        total == mip.xsum(c[j] * X[j] for j in range(n)),
        name="profit",
    )

    model.objective = total
    return model, {"total_profit": total, "x": X}
