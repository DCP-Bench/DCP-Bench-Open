import pulp

# The reference's own domain for x.
LOW, HIGH = 0, 7


def build(instance):
    n, wanted, values = instance["n"], instance["m"], instance["v"]
    domain = range(LOW, HIGH + 1)
    problem = pulp.LpProblem("among", pulp.LpMinimize)
    x = [pulp.LpVariable(f"x_{i}", LOW, HIGH, cat="Integer") for i in range(n)]
    # takes[i][d] is 1 exactly when x[i] is d.
    takes = [{d: pulp.LpVariable(f"takes_{i}_{d}", cat="Binary") for d in domain} for i in range(n)]
    for i in range(n):
        problem += pulp.lpSum(takes[i].values()) == 1
        problem += x[i] == pulp.lpSum(d * takes[i][d] for d in domain)
    problem += pulp.lpSum(takes[i][d] for i in range(n) for d in values) == wanted
    return problem, {"x": x}
