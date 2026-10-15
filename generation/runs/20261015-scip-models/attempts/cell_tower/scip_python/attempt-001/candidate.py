# Cell tower coverage: choose which candidate sites get a tower, within budget,
# to maximise the population covered by at least one chosen tower.

from pyscipopt import Model, quicksum


def build(instance):
    cost = instance["cost"]          # cost[i] of building a tower at site i
    delta = instance["delta"]        # delta[i][r] = 1 if site i covers region r
    population = instance["population"]  # population[r] of region r
    budget = instance["budget"]      # total cost the company can spend

    n_sites = len(cost)
    n_regions = len(population)

    m = Model("cell_tower")

    # build[i] = 1 if a tower is built at site i
    build = [m.addVar(name=f"build_{i}", vtype="B") for i in range(n_sites)]
    # covered[r] = 1 if region r is covered by at least one built tower
    covered = [m.addVar(name=f"covered_{r}", vtype="B") for r in range(n_regions)]

    # the total cost of the built towers must not exceed the budget
    m.addCons(quicksum(cost[i] * build[i] for i in range(n_sites)) <= budget)

    # a region counts as covered only if a tower covering it is built
    for r in range(n_regions):
        # region r is covered only if some site that covers it gets a tower
        m.addCons(covered[r] <= quicksum(delta[i][r] * build[i] for i in range(n_sites)))

    # the objective is the total population covered
    total_population_covered = quicksum(population[r] * covered[r] for r in range(n_regions))
    m.setObjective(total_population_covered, "maximize")

    return m, {
        "build_tower": build,
        "total_population_covered": total_population_covered,
    }
