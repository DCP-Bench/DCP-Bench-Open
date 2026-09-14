import pulp


def build(instance):
    attributes, required = instance["attributes"], instance["required_crew"]
    persons, flights = range(len(attributes)), range(len(required))
    skills = range(len(required[0]) - 1)
    problem = pulp.LpProblem("crew", pulp.LpMinimize)
    assigned = [[pulp.LpVariable(f"crew_{f}_{p}", cat="Binary") for p in persons] for f in flights]
    for f in flights:
        problem += pulp.lpSum(assigned[f]) == required[f][0]
        for j in skills:
            problem += pulp.lpSum(attributes[p][j] * assigned[f][p] for p in persons) >= required[f][j + 1]
    # After a flight, a break of at least two flights.
    for f in range(len(required) - 2):
        for p in persons:
            problem += assigned[f][p] + assigned[f + 1][p] + assigned[f + 2][p] <= 1
    return problem, {"crew": assigned}
