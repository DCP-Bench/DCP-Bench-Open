# Cell tower coverage: choose the sites to build towers on, within the budget,
# so that the regions covered by at least one built tower hold as many people
# as possible.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    delta = instance["delta"]            # delta[i][j] = 1 if site i covers region j
    cost = instance["cost"]
    population = instance["population"]
    budget = instance["budget"]
    num_sites = len(cost)
    num_regions = len(population)

    pool = IDPool()
    # build_tower[i] is true when a tower is built at site i.
    build_tower = [pool.id(("build_tower", i)) for i in range(num_sites)]
    # covered_region[j] is true when region j counts as covered.
    covered_region = [pool.id(("covered_region", j)) for j in range(num_regions)]

    formula = WCNF()

    # A region is covered only if at least one site covering it gets a tower.
    for j in range(num_regions):
        formula.append([-covered_region[j]]
                       + [build_tower[i] for i in range(num_sites) if delta[i][j] > 0])

    # The total cost of the towers built does not exceed the budget.
    formula.extend(PBEnc.leq(lits=build_tower, weights=cost, bound=budget,
                             vpool=pool).clauses)

    # total_population_covered is the population of the covered regions. Its
    # domain runs from the sum of the negative populations to the sum of the
    # positive ones, the most any choice of regions can reach.
    low = sum(p for p in population if p < 0)
    high = sum(p for p in population if p > 0)
    total = Integer("total_population_covered", low, max(high, low + 1), vpool=pool)
    # Its domain clauses (exactly one value) come from the engine.
    formula.extend(IntegerEngine(vars=[total], vpool=pool).clausify().clauses)

    # The total is tied to the covered regions by a running sum over the
    # regions, one literal per partial sum that can occur. A linear constraint
    # over a domain this wide (thousands of values) would give the encoder
    # thousands of weighted literals; the running sum stays as small as the
    # number of distinct partial sums, and unit propagation fixes the total
    # once the covered regions are fixed.
    # partial[v] is true when the regions considered so far sum to v.
    start = pool.id(("partial", 0, 0))
    formula.append([start])
    partial = {0: start}
    for j in range(num_regions):
        nxt = {}
        for v in partial:
            for w in (v, v + population[j]):
                if w not in nxt:
                    nxt[w] = pool.id(("partial", j + 1, w))
        for v, lit in partial.items():
            # region j uncovered: the sum stays at v; covered: it grows by its population
            formula.append([-lit, covered_region[j], nxt[v]])
            formula.append([-lit, -covered_region[j], nxt[v + population[j]]])
        partial = nxt
    # The final partial sum is the total; the total takes exactly one value,
    # so exactly one final partial sum is true, and with it one per region.
    for v, lit in partial.items():
        formula.append([-lit, total.equals(v)])
    for v in range(low, max(high, low + 1) + 1):
        if v not in partial:
            formula.append([-total.equals(v)])

    # Maximise the population covered: leaving region j uncovered pays its
    # population, so RC2 minimises the shortfall from the sum of all positive
    # populations. A region with a negative population pays when it is covered.
    for j in range(num_regions):
        if population[j] > 0:
            formula.append([covered_region[j]], weight=population[j])
        elif population[j] < 0:
            formula.append([-covered_region[j]], weight=-population[j])

    return formula, {"build_tower": build_tower,
                     "total_population_covered": total}
