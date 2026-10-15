# Bus driver scheduling (CSPLib 022): choose a set of shifts so that every piece
# of work is covered exactly once, minimising the number of shifts chosen.
from pyscipopt import Model, quicksum


def build(instance):
    num_work = instance["num_work"]
    shifts = instance["shifts"]  # shifts[j] lists the work pieces (0-based) that shift j covers
    num_shifts = len(shifts)

    m = Model()

    # x[j] = 1 if shift j is selected
    x = [m.addVar(name=f"x_{j}", vtype="B") for j in range(num_shifts)]

    # Each piece of work is covered by exactly one selected shift
    covering = [[] for _ in range(num_work)]
    for j, tasks in enumerate(shifts):
        for i in tasks:
            covering[i].append(j)
    for i in range(num_work):
        # work piece i is covered exactly once
        m.addCons(quicksum(x[j] for j in covering[i]) == 1)

    # Minimise the number of selected shifts (all shifts cost the same)
    m.setObjective(quicksum(x), "minimize")

    return m, {"x": x}
