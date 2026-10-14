"""Cell towers: choose tower sites within the budget so that the covered population is as large as possible."""
from docplex.mp.model import Model


def build(instance):
    delta = instance["delta"]  # delta[i][j] is 1 if a tower at site i covers region j
    cost = instance["cost"]
    population = instance["population"]
    sites = range(len(cost))
    regions = range(len(population))

    model = Model("cell_tower")

    # build_tower[i] is 1 when a tower is built at site i;
    # covered[j] is 1 when region j counts as covered.
    build_tower = model.binary_var_list(len(cost), name="build_tower")
    covered = model.binary_var_list(len(population), name="covered")

    # A region is covered only if at least one tower that covers it is built.
    for j in regions:
        model.add_constraint(covered[j] <= model.sum(delta[i][j] * build_tower[i] for i in sites),
                             ctname=f"coverage_{j}")

    # The towers built cost no more than the budget.
    model.add_constraint(model.dot(build_tower, cost) <= instance["budget"], ctname="budget")

    # Maximise the population of the covered regions.
    total_population_covered = model.dot(covered, population)
    model.maximize(total_population_covered)

    return model, {"build_tower": build_tower, "total_population_covered": total_population_covered}
