# Set covering: hire a set of workers of minimum total cost so that every task
# is performed by at least one hired worker who is qualified for it.
from pyscipopt import Model, quicksum


def build(instance):
    nb_workers = instance["nb_workers"]
    cost = instance["Cost"]
    # Qualified[t] lists the workers (numbered from 1) who can perform task t.
    qualified = instance["Qualified"]

    m = Model()
    # hired[w] = 1 if worker w is hired (workers are numbered from 0 here)
    hired = [m.addVar(name=f"hired_{w}", vtype="B") for w in range(nb_workers)]

    # every task is performed: at least one qualified worker for it is hired
    for t, workers in enumerate(qualified):
        m.addCons(quicksum(hired[w - 1] for w in workers) >= 1, name=f"task_{t + 1}")

    # the total hiring cost of the selected workers, to be minimised
    total_cost = quicksum(cost[w] * hired[w] for w in range(nb_workers))
    m.setObjective(total_cost, "minimize")

    return m, {"total_cost": total_cost, "workers": hired}
