"""Scheduling: four tasks on one machine, precedence and release times, minimise makespan.

Two tasks that share the machine must not overlap. Each order is a reified
condition, and at least one of the two must hold.
"""
from exact import Exact

NAMES = ["cut", "weld", "paint", "pack"]
DURATION = [3, 2, 4, 2]
RELEASE = [0, 0, 5, 0]
PRECEDES = [(0, 2)]  # task 0 must finish before task 2 starts

solver = Exact()
start = [f"start_{n}" for n in NAMES]
for i, name in enumerate(NAMES):
    solver.addVariable(start[i], RELEASE[i], 30)
solver.addVariable("makespan", 0, 30)

for i in range(len(NAMES)):
    # makespan >= start_i + duration_i
    solver.addConstraint([(1, "makespan"), (-1, start[i])], True, DURATION[i])

for i, j in PRECEDES:
    solver.addConstraint([(1, start[j]), (-1, start[i])], True, DURATION[i])

for i in range(len(NAMES)):
    for j in range(i + 1, len(NAMES)):
        i_first = f"i_before_{i}_{j}"
        j_first = f"j_before_{i}_{j}"
        solver.addVariable(i_first, 0, 1)
        solver.addVariable(j_first, 0, 1)
        # i_first <-> start_j - start_i >= duration_i
        solver.addReification(i_first, True,
                              [(1, start[j]), (-1, start[i])], DURATION[i])
        # j_first <-> start_i - start_j >= duration_j
        solver.addReification(j_first, True,
                              [(1, start[i]), (-1, start[j])], DURATION[j])
        solver.addConstraint([(1, i_first), (1, j_first)], True, 1)

solver.setObjective([(1, "makespan")], minimize=True)
state, value = solver.toOptimum()
if state == "SAT":
    starts = solver.getLastSolutionFor(start)
    print("status:", state)
    print("Makespan:", value)
    for name, s in zip(NAMES, starts):
        print(f"{name} starts at {s}")
else:
    print("status:", state)
