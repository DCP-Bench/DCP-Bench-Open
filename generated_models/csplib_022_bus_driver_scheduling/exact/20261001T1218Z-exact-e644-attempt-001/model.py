# Bus driver scheduling: choose a set of shifts, each covering some pieces of work, so that
# every piece of work is covered by exactly one chosen shift, using as few shifts as possible.
from exact import Exact


def build(instance):
    num_work = instance["num_work"]  # pieces of work (tasks) to cover
    num_shifts = instance["num_shifts"]  # candidate shifts
    shifts = instance["shifts"]  # shifts[i] = the tasks that shift i covers

    solver = Exact()

    # x[i] = 1 when shift i is selected
    x = [f"x_{i}" for i in range(num_shifts)]
    for name in x:
        solver.addVariable(name, 0, 1)

    # every task is covered by exactly one selected shift (set partitioning)
    for t in range(num_work):
        covering = [(1, x[i]) for i in range(num_shifts) if t in shifts[i]]
        solver.addConstraint(covering, True, 1, True, 1)

    # use as few shifts as possible; every shift costs the same
    return solver, {"x": x}, ("minimize", [(1, name) for name in x])
