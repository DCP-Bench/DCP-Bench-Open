import pulp


def build(instance):
    n = instance["n"]
    problem = pulp.LpProblem("smoke", pulp.LpMinimize)
    x = pulp.LpVariable("x", 0, n, cat="Integer")
    y = pulp.LpVariable("y", 0, n, cat="Integer")
    if instance["optimize"]:
        problem += x + y >= n
        problem += x + y
    else:
        problem += x + y == n
    return problem, {"x": x, "y": y}
