# Build towers within budget to cover the most people.
from dcp_maxsat import MaxSat


def reachable(weights):
    """Every total a subset of these weights can add up to."""
    totals = {0}
    for weight in weights:
        totals |= {total + weight for total in totals}
    return sorted(totals)


def build(instance):
    delta = instance["delta"]
    cost = instance["cost"]
    population = instance["population"]
    budget = instance["budget"]
    sites, regions = len(cost), len(population)

    sat = MaxSat()
    build_tower = sat.bools(sites)
    covered = sat.bools(regions)

    # A region only counts as covered if some chosen site reaches it.
    for j in range(regions):
        reach = [delta[i][j] for i in range(sites)]
        sat.bool_sum_ge(reach + [-1], build_tower + [covered[j]], 0)
    sat.bool_sum_le(cost, build_tower, budget)

    reached = sat.int_from(reachable(population))
    sat.link_bool_sum(population, covered, reached)
    return sat, {"build_tower": build_tower,
                 "total_population_covered": reached}, ("maximize", reached)
