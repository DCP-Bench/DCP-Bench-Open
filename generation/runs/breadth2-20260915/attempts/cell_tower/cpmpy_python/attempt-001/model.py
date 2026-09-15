import cpmpy as cp


def build(instance):
    delta, cost = instance["delta"], instance["cost"]
    population, budget = instance["population"], instance["budget"]
    sites, regions = len(cost), len(population)
    build_tower = cp.boolvar(shape=sites, name="build_tower")
    covered = cp.boolvar(shape=regions, name="covered")
    model = cp.Model()
    for j in range(regions):
        model += covered[j] <= cp.sum([delta[i][j] * build_tower[i] for i in range(sites)])
    model += cp.sum([cost[i] * build_tower[i] for i in range(sites)]) <= budget
    reached = cp.sum([population[j] * covered[j] for j in range(regions)])
    model.maximize(reached)
    return model, {"build_tower": [build_tower[i] for i in range(sites)],
                   "total_population_covered": reached}
