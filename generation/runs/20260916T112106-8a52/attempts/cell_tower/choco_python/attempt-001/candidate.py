from pychoco.model import Model


def build(instance):
    """Cell tower siting: build towers within budget so as to cover the largest
    population.  A region counts as covered only if some built site reaches it.
    """
    delta = instance["delta"]
    cost = instance["cost"]
    population = instance["population"]
    budget = instance["budget"]
    sites = len(cost)
    regions = len(population)

    model = Model()
    build_tower = [model.boolvar(name=f"t{i}") for i in range(sites)]
    covered = [model.boolvar(name=f"c{j}") for j in range(regions)]

    for j in range(regions):
        # A region may only count as covered if some built site reaches it.
        reach = [delta[i][j] for i in range(sites)]
        model.scalar(build_tower + [covered[j]], reach + [-1], ">=", 0).post()

    model.scalar(build_tower, cost, "<=", budget).post()

    total = model.intvar(0, sum(population), name="total")
    model.scalar(covered, population, "=", total).post()

    return model, {
        "build_tower": build_tower, "total_population_covered": total,
    }, ("maximize", total)
