# Build towers within budget to cover the most people.
from exact import Exact


def build(instance):
    delta = instance["delta"]
    cost = instance["cost"]
    population = instance["population"]
    budget = instance["budget"]
    sites, regions = len(cost), len(population)

    solver = Exact()
    build_tower = [f"t{i}" for i in range(sites)]
    covered = [f"cov{j}" for j in range(regions)]
    for name in build_tower + covered:
        solver.addVariable(name, 0, 1)

    # A region only counts as covered if some chosen site reaches it.
    for j in range(regions):
        reach = [(delta[i][j], build_tower[i]) for i in range(sites)]
        solver.addConstraint(reach + [(-1, covered[j])], True, 0)
    solver.addConstraint(list(zip(cost, build_tower)), False, 0, True, budget)

    solver.addVariable("reached", 0, sum(population))
    solver.addConstraint(list(zip(population, covered)) + [(-1, "reached")],
                         True, 0, True, 0)
    return (solver,
            {"build_tower": build_tower, "total_population_covered": "reached"},
            ("maximize", [(1, "reached")]))
