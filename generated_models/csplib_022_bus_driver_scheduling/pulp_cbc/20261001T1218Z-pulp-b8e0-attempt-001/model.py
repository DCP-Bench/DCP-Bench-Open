"""Bus driver scheduling: choose a set of shifts, each covering a subset of the pieces of
work, so that every piece of work is covered by exactly one chosen shift and as few
shifts as possible are used (every shift costs the same).

The model reports which shifts are chosen.
"""
import pulp


def build(instance):
    num_work = instance["num_work"]  # number of pieces of work (tasks)
    num_shifts = instance["num_shifts"]  # number of candidate shifts
    shifts = instance["shifts"]  # shifts[i] = the tasks covered by shift i

    problem = pulp.LpProblem("bus_driver_scheduling", pulp.LpMinimize)

    # x[i] = 1 if shift i is chosen
    x = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(num_shifts)]

    # objective: use as few shifts as possible
    problem += pulp.lpSum(x)

    # every piece of work is covered by exactly one chosen shift (set partitioning)
    for task in range(num_work):
        problem += pulp.lpSum(x[i] for i in range(num_shifts) if task in shifts[i]) == 1

    return problem, {"x": x}
