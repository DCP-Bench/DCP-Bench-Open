"""Cell towers: choose tower sites within the budget so that the covered population is as large as possible."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    delta = instance["delta"]  # delta[i][j] is 1 if a tower at site i covers region j
    cost = instance["cost"]
    population = instance["population"]
    sites = range(len(cost))
    regions = range(len(population))

    model = gp.Model("cell_tower")

    # build_tower[i] is 1 when a tower is built at site i;
    # covered[j] is 1 when region j counts as covered.
    build_tower = model.addVars(sites, vtype=GRB.BINARY, name="build_tower")
    covered = model.addVars(regions, vtype=GRB.BINARY, name="covered")

    # A region is covered only if at least one tower that covers it is built.
    for j in regions:
        model.addConstr(covered[j] <= gp.quicksum(delta[i][j] * build_tower[i] for i in sites),
                        name=f"coverage[{j}]")

    # The towers built cost no more than the budget.
    model.addConstr(gp.quicksum(cost[i] * build_tower[i] for i in sites) <= instance["budget"],
                    name="budget")

    # Maximise the population of the covered regions.
    total_population_covered = gp.quicksum(population[j] * covered[j] for j in regions)
    model.setObjective(total_population_covered, GRB.MAXIMIZE)

    return model, {"build_tower": [build_tower[i] for i in sites],
                   "total_population_covered": total_population_covered}
