# Cell tower coverage: choose which potential tower sites to build so that
# the largest population is covered, within the tower budget.
# Source: instance fields cost, budget, delta (site-region reach), population.
from paramita.modelling import Bool, Iff, Or


def build(instance):
    cost = instance["cost"]
    budget = instance["budget"]
    population = instance["population"]
    delta = instance["delta"]
    n_sites = len(cost)
    n_regions = len(population)

    # one Bool per potential site: 1 if a tower is built there
    build_tower = [Bool(f"build_{i}") for i in range(n_sites)]
    cons = []

    # only a limited number of towers can be built: the total cost stays within the budget
    cons.append(sum(cost[i] * build_tower[i] for i in range(n_sites)) <= budget)

    # a region is covered exactly when at least one built tower reaches it
    covered = []
    for r in range(n_regions):
        c = Bool(f"covered_{r}")
        reaching = [build_tower[i] for i in range(n_sites) if delta[i][r]]
        if not reaching:
            cons.append(~c)
        elif len(reaching) == 1:
            cons.append(Iff(c, reaching[0]))
        else:
            cons.append(Iff(c, Or(reaching)))
        covered.append(c)

    # the population covered by the built towers, to be maximised
    total = sum(population[r] * covered[r] for r in range(n_regions))
    return cons, {"build_tower": build_tower, "total_population_covered": total}, ("maximize", total)
