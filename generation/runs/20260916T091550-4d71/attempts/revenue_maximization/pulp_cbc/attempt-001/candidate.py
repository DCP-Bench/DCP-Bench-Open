import pulp


def build(instance):
    """Revenue maximization: sell fare packages within each package's demand
    and each flight leg's seat count, for the most revenue.
    """
    available_seats = instance["available_seats"]
    demand = instance["demand"]
    revenue = instance["revenue"]
    delta = instance["delta"]
    packages = len(demand)
    legs = len(available_seats)
    max_demand = max(demand)

    problem = pulp.LpProblem("revenue", pulp.LpMaximize)
    sell = [pulp.LpVariable(f"sell{i}", 0, max_demand, cat="Integer")
            for i in range(packages)]

    for j in range(legs):
        problem += pulp.lpSum(delta[i][j] * sell[i] for i in range(packages)) <= available_seats[j]
    for i in range(packages):
        problem += sell[i] <= demand[i]

    bound = sum(revenue[i] * demand[i] for i in range(packages))
    max_revenue = pulp.LpVariable("max_revenue", 0, bound, cat="Integer")
    problem += max_revenue == pulp.lpSum(revenue[i] * sell[i] for i in range(packages))
    problem += max_revenue

    return problem, {"packages_to_sell": sell, "max_revenue": max_revenue}
