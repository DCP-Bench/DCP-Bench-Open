# Cell tower coverage: choose which potential tower sites to build, under a budget,
# so that the population covered by the towers is as large as possible (maximise).

import mip


def build(instance):
    cost = instance["cost"]
    delta = instance["delta"]
    population = instance["population"]
    budget = instance["budget"]

    n_sites = len(cost)
    n_regions = len(population)

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # Decision: build a tower at each potential site.
    build_tower = [model.add_var(f"build_{s}", var_type=mip.BINARY) for s in range(n_sites)]

    # Auxiliary: a region is covered by at least one built tower.
    covered = [model.add_var(f"covered_{r}", var_type=mip.BINARY) for r in range(n_regions)]

    # A region is covered only if some built tower reaches it (delta[s][r] = 1 when site s covers region r).
    for r in range(n_regions):
        model += covered[r] <= mip.xsum(delta[s][r] * build_tower[s] for s in range(n_sites))

    # The total cost of the built towers stays within the budget.
    model += mip.xsum(cost[s] * build_tower[s] for s in range(n_sites)) <= budget

    # The total population covered is the sum of the populations of the covered regions.
    total = model.add_var("total_population_covered", var_type=mip.INTEGER, lb=0,
                          ub=sum(population))
    model += total == mip.xsum(population[r] * covered[r] for r in range(n_regions))

    model.objective = total

    return model, {"build_tower": build_tower, "total_population_covered": total}
