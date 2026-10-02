# Bus driver scheduling: pick the fewest shifts such that every piece of work is
# covered by exactly one chosen shift (a set partitioning problem).
import z3


def build(instance):
    num_work = instance["num_work"]      # number of tasks (pieces of work)
    num_shifts = instance["num_shifts"]  # number of candidate shifts
    shifts = instance["shifts"]          # shifts[i]: the tasks that shift i covers

    # x[i] is true if shift i is selected.
    x = [z3.Bool(f"x_{i}") for i in range(num_shifts)]

    solver = z3.Solver()

    # Every task is covered by exactly one selected shift.
    for task in range(num_work):
        covering = [x[i] for i in range(num_shifts) if task in shifts[i]]
        if covering:
            solver.add(z3.PbEq([(s, 1) for s in covering], 1))
        else:
            solver.add(z3.BoolVal(False))  # no shift covers this task: no schedule exists

    # Use as few shifts as possible (every shift costs the same).
    return solver, {"x": x}, ("minimize", z3.Sum([z3.If(s, 1, 0) for s in x]))
