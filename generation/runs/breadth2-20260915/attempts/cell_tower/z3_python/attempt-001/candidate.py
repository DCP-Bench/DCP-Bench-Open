import z3


def build(instance):
    delta, cost = instance["delta"], instance["cost"]
    population, budget = instance["population"], instance["budget"]
    sites, regions = len(cost), len(population)
    build_tower = [z3.Bool(f"b_{i}") for i in range(sites)]
    covered = [z3.Bool(f"c_{j}") for j in range(regions)]
    built = [z3.If(build_tower[i], 1, 0) for i in range(sites)]
    reaches = [z3.If(covered[j], 1, 0) for j in range(regions)]
    constraints = [reaches[j] <= z3.Sum([delta[i][j] * built[i] for i in range(sites)])
                   for j in range(regions)]
    constraints.append(z3.Sum([cost[i] * built[i] for i in range(sites)]) <= budget)
    reached = z3.Sum([population[j] * reaches[j] for j in range(regions)])
    return constraints, {"build_tower": build_tower, "total_population_covered": reached}, \
        ("maximize", reached)
