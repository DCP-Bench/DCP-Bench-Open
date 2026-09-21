# Build towers within budget to cover the most people.
from dcp_pb import Pb


def build(instance):
    delta = instance["delta"]
    cost = instance["cost"]
    population = instance["population"]
    budget = instance["budget"]
    sites, regions = len(cost), len(population)

    pb = Pb()
    build_tower = pb.bools(sites)
    covered = pb.bools(regions)

    # A region only counts as covered if some chosen site reaches it.
    for j in range(regions):
        reach = [(delta[i][j], build_tower[i]) for i in range(sites)]
        pb.ge(reach + [(-1, covered[j])], 0)
    pb.weighted_sum_le(cost, build_tower, budget)

    reached = pb.int(0, sum(population))
    pb.eq(list(zip(population, covered)) + [(-1, reached)], 0)
    pb.maximise([(1, reached)])
    return pb, {"build_tower": build_tower,
                "total_population_covered": reached}
