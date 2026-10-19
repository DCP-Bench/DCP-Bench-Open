# Cell tower coverage (cvc5 pythonic model).
# Choose which candidate tower sites to build so that the total population
# covered by the built towers is maximal, under a budget on the tower costs.
import cvc5.pythonic as cz


def build(instance):
    cost = instance["cost"]
    population = instance["population"]
    delta = instance["delta"]
    budget = instance["budget"]
    n_sites = len(cost)
    n_regions = len(population)

    # A tower is built or not at each site.
    build_tower = cz.Bools([f"build_{s}" for s in range(n_sites)])
    # A region is covered when at least one built tower reaches it.
    covered = cz.Bools([f"covered_{r}" for r in range(n_regions)])

    constraints = []

    # The description says only a limited number of towers can be built within the budget.
    constraints.append(
        cz.Sum([cz.If(build_tower[s], cost[s], 0) for s in range(n_sites)]) <= budget
    )

    # A region is covered exactly when a built tower covers it.
    for r in range(n_regions):
        reaching = [build_tower[s] for s in range(n_sites) if delta[s][r] == 1]
        if not reaching:
            constraints.append(covered[r] == cz.BoolVal(False))
        elif len(reaching) == 1:
            constraints.append(covered[r] == reaching[0])
        else:
            constraints.append(covered[r] == cz.Or(reaching))

    # The objective is the total population of the covered regions.
    total = cz.Sum([cz.If(covered[r], population[r], 0) for r in range(n_regions)])

    outputs = {
        "build_tower": [build_tower[s] for s in range(n_sites)],
        "total_population_covered": total,
    }
    return constraints, outputs, ("maximize", total)
