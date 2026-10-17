# Set covering (covering_opl): select a set of workers so that every task is
# performed by a hired worker qualified for it, minimising the total hiring cost.
# Outputs: total_cost (int) and workers (one Boolean per worker, True if hired).

import cvc5.pythonic as cz


def build(instance):
    n = instance["nb_workers"]
    cost = instance["Cost"]
    qualified = instance["Qualified"]

    # One Boolean per worker: hired or not.
    hired = [cz.Bool(f"hired_{i}") for i in range(n)]

    constraints = []

    # Ensure that all tasks are performed.
    for task in qualified:
        # Qualified worker indices are 1-based in the data.
        lits = [hired[w - 1] for w in task]
        constraints.append(lits[0] if len(lits) == 1 else cz.Or(lits))

    # Each worker has a hiring cost; the total cost of the hired workers is minimised.
    total = cz.Sum([cz.If(hired[i], cost[i], 0) for i in range(n)])

    return constraints, {"total_cost": total, "workers": hired}, ("minimize", total)
