# Build towers within budget to cover the most people.
from hermax.model import Model


def build(instance):
    delta = instance["delta"]
    cost = instance["cost"]
    population = instance["population"]
    budget = instance["budget"]
    sites, regions = len(cost), len(population)

    m = Model()
    build_tower = m.bool_vector("build_tower", sites)
    covered = m.bool_vector("covered", regions)

    # A region only counts as covered if some chosen site reaches it.
    for j in range(regions):
        m &= (sum(delta[i][j] * build_tower[i] for i in range(sites)) >= covered[j])
    m &= (sum(cost[i] * build_tower[i] for i in range(sites)) <= budget)

    # Maximising the reach: every region left uncovered costs its population.
    for j in range(regions):
        m.obj[population[j]] += covered[j]

    reached = m.int("total_population_covered", 0, sum(population))
    m &= (sum(population[j] * covered[j] for j in range(regions)) == reached)
    return m, {"build_tower": build_tower, "total_population_covered": reached}
