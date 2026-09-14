import pulp


def build(instance):
    delta, cost = instance["delta"], instance["cost"]
    population, budget = instance["population"], instance["budget"]
    sites, regions = range(len(cost)), range(len(population))
    problem = pulp.LpProblem("cell_tower", pulp.LpMaximize)
    build_tower = [pulp.LpVariable(f"build_{i}", cat="Binary") for i in sites]
    covered = [pulp.LpVariable(f"covered_{j}", cat="Binary") for j in regions]
    for j in regions:
        problem += covered[j] <= pulp.lpSum(delta[i][j] * build_tower[i] for i in sites)
    problem += pulp.lpSum(cost[i] * build_tower[i] for i in sites) <= budget
    reached = pulp.lpSum(population[j] * covered[j] for j in regions)
    problem += reached
    return problem, {"build_tower": build_tower, "total_population_covered": reached}
