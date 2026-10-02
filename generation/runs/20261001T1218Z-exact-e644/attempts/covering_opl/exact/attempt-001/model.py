# Covering (OPL): hire a set of workers of minimum total cost such that every task has at
# least one hired worker who is qualified for it.
from exact import Exact


def build(instance):
    nb_workers = instance["nb_workers"]
    qualified = instance["Qualified"]  # qualified[j] = the (1-based) workers able to do task j
    cost = instance["Cost"]  # hiring cost of each worker
    num_tasks = len(qualified)

    solver = Exact()

    # workers[i] = 1 when worker i is hired
    workers = [f"workers_{i}" for i in range(nb_workers)]
    for name in workers:
        solver.addVariable(name, 0, 1)

    # total_cost is the summed hiring cost of the hired workers (its upper bound, as in the
    # reference, is nb_workers * the sum of all costs)
    solver.addVariable("total_cost", 0, nb_workers * sum(cost))
    hiring = [(cost[i], workers[i]) for i in range(nb_workers) if cost[i]]
    solver.addConstraint(hiring + [(-1, "total_cost")], True, 0, True, 0)

    # every task is done by at least one hired worker among those qualified for it
    # (the data numbers workers from 1, the variables from 0)
    for j in range(num_tasks):
        able = sorted(set(q - 1 for q in qualified[j]))
        solver.addConstraint([(1, workers[i]) for i in able], True, 1)

    # minimise the total hiring cost
    return solver, {"total_cost": "total_cost", "workers": workers}, ("minimize", hiring)
