from ortools.sat.python import cp_model


def build(instance):
    delta, cost = instance["delta"], instance["cost"]
    population, budget = instance["population"], instance["budget"]
    sites, regions = len(cost), len(population)
    model = cp_model.CpModel()
    build_tower = [model.new_bool_var(f"b_{i}") for i in range(sites)]
    covered = [model.new_bool_var(f"c_{j}") for j in range(regions)]
    for j in range(regions):
        model.add(covered[j] <= sum(delta[i][j] * build_tower[i] for i in range(sites)))
    model.add(sum(cost[i] * build_tower[i] for i in range(sites)) <= budget)
    reached = sum(population[j] * covered[j] for j in range(regions))
    model.maximize(reached)
    return model, {"build_tower": build_tower, "total_population_covered": reached}
