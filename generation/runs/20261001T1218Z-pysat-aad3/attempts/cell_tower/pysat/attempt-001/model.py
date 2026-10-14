# Cell tower placement: build towers on sites within a budget so that the population living in
# covered regions is as large as possible.
# PySAT only decides satisfiability, so the covered population to maximise is returned as
# the objective (the runner refuses a returned objective instead of ignoring it).
from pysat.formula import CNF, IDPool
from pysat.pb import PBEnc


def build(instance):
    delta = instance["delta"]            # delta[i][j] = 1 if site i covers region j
    cost = instance["cost"]              # cost of building a tower at site i
    population = instance["population"]  # inhabitants of region j
    budget = instance["budget"]
    n_sites, n_regions = len(cost), len(population)

    pool = IDPool()
    cnf = CNF()
    build_tower = [pool.id(("build", i)) for i in range(n_sites)]
    covered = [pool.id(("covered", j)) for j in range(n_regions)]

    # a region counts as covered only if a tower is built on a site that covers it
    for j in range(n_regions):
        cnf.append([-covered[j]] + [build_tower[i] for i in range(n_sites) if delta[i][j]])
    # the towers must not cost more than the budget
    cnf.extend(PBEnc.leq(lits=build_tower, weights=cost, bound=budget, vpool=pool).clauses)

    return cnf, {"build_tower": build_tower}, ("maximize", covered, population)
