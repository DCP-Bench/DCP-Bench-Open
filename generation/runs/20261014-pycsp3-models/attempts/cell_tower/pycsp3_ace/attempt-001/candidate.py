from pycsp3 import *

# choose which cell tower sites to build so that the largest population is covered within the budget
n_sites = len(data.cost)
n_regions = len(data.population)
# build_tower[s] is 1 if a tower is built at site s
build_tower = VarArray(size=n_sites, dom={0, 1})
# covered[r] is 1 if region r receives signal
covered = VarArray(size=n_regions, dom={0, 1})
# total population covered by the built towers
total_population_covered = Var(dom=range(sum(data.population) + 1))
satisfy(
    # the towers built must fit within the budget
    Sum(data.cost[s] * build_tower[s] for s in range(n_sites)) <= data.budget,
    # a region is covered only when a tower built at a site that reaches it
    [covered[r] <= Sum(build_tower[s] * data.delta[s][r] for s in range(n_sites)) for r in range(n_regions)],
    # a region is covered when any tower that reaches it is built
    [covered[r] >= build_tower[s] for s in range(n_sites) for r in range(n_regions) if data.delta[s][r] == 1],
    # the total population covered is the sum of the populations of the covered regions
    total_population_covered == Sum(data.population[r] * covered[r] for r in range(n_regions)),
)
# maximise the total population covered
maximize(total_population_covered)
