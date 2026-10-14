"""Equal-sized groups: split a sorted list into k groups at k - 1 break points, keeping equal values together, with sizes as close to n / k as possible."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    a, k = instance["a"], instance["k"]
    n = len(a)
    ideal = round(n / k)  # the ideal group size, rounded as Python rounds, like the reference
    groups = range(k)
    breaks = range(k - 1)

    # A break point j (1-based: the first j elements lie before it) may not
    # separate two equal values, so it can only sit where the value changes.
    # The reference also leaves j = n unconstrained.
    allowed = [j for j in range(1, n) if a[j - 1] != a[j]] + [n]

    model = gp.Model("equal_sized_groups")

    # at[p, j] is 1 when break point p is at position j. Choosing among the
    # allowed positions encodes "equal values stay in one group" directly,
    # instead of forbidding each of the many other positions one by one.
    at = model.addVars(breaks, allowed, vtype=GRB.BINARY, name="at")
    for p in breaks:
        model.addConstr(at.sum(p, "*") == 1, name=f"one_position[{p}]")
    x = [gp.quicksum(j * at[p, j] for j in allowed) for p in breaks]

    # size[i] is the number of elements in group i, at least 1 as in the reference:
    # the first group ends at the first break point, each later one at the next,
    # and the last runs to the end of the list.
    size = model.addVars(groups, lb=1, ub=n, vtype=GRB.INTEGER, name="size")
    model.addConstr(size[0] == x[0], name="first_group")
    for i in range(1, k - 1):
        model.addConstr(size[i] == x[i] - x[i - 1], name=f"group[{i}]")
    model.addConstr(size[k - 1] == n - x[k - 2], name="last_group")

    # error[i] is at least the distance of group i's size from the ideal size;
    # since the total is minimised, each is exactly that distance at the optimum.
    error = model.addVars(groups, lb=0, ub=n, vtype=GRB.INTEGER, name="error")
    for i in groups:
        model.addConstr(error[i] >= size[i] - ideal, name=f"over[{i}]")
        model.addConstr(error[i] >= ideal - size[i], name=f"under[{i}]")

    # The total error, which the reference bounds to 0..n, is minimised.
    total_error = error.sum()
    model.addConstr(total_error <= n, name="error_domain")
    model.setObjective(total_error, GRB.MINIMIZE)

    return model, {"x": x}
