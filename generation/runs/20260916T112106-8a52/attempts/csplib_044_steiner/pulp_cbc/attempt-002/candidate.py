import itertools

import pulp


def build(instance):
    """Steiner triple system: n(n-1)/6 triples drawn from n items, no two
    triples sharing more than one item.

    Two triples share at most one item exactly when no pair of items appears in
    two different triples. Stating it that way needs one indicator per triple
    and pair rather than one per pair of triples and item, and the pair count
    is the real combinatorial structure, so the relaxation is far tighter --
    the per-triple-pair encoding times out on the larger instances.
    """
    n = instance["n"]
    n_sets = n * (n - 1) // 6

    problem = pulp.LpProblem("steiner", pulp.LpMinimize)
    sets = pulp.LpVariable.dicts("sets", (range(n_sets), range(n)),
                                 cat="Binary")

    for i in range(n_sets):
        problem += pulp.lpSum(sets[i][j] for j in range(n)) == 3

    for u, v in itertools.combinations(range(n), 2):
        covers = []
        for i in range(n_sets):
            together = pulp.LpVariable(f"pair_{i}_{u}_{v}", cat="Binary")
            problem += together >= sets[i][u] + sets[i][v] - 1
            problem += together <= sets[i][u]
            problem += together <= sets[i][v]
            covers.append(together)
        # Each pair of items lies in at most one triple.
        problem += pulp.lpSum(covers) <= 1

    rows = [[sets[i][j] for j in range(n)] for i in range(n_sets)]
    return problem, {"sets": rows}
