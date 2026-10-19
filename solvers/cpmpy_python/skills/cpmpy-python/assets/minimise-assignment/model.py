"""Assign four tasks to four workers, one task each, minimising the total cost."""
import cpmpy as cp
from cpmpy.solvers.solver_interface import ExitStatus

cost = [[9, 2, 7, 8],
        [6, 4, 3, 7],
        [5, 8, 1, 8],
        [7, 6, 9, 4]]
n = len(cost)

worker = cp.intvar(0, n - 1, shape=n, name="worker")  # worker assigned to each task
model = cp.Model(cp.AllDifferent(worker))             # at most one task per worker
# cost[t] is a plain Python list indexed by a decision variable: wrap it in cp.cpm_array
model.minimize(cp.sum(cp.cpm_array(cost[t])[worker[t]] for t in range(n)))

if model.solve():
    assignment = [int(w.value()) for w in worker]
    print("Worker per task:", assignment)
    print("Cost:", int(model.objective_value()))
    print("Proven optimal:", model.status().exitstatus == ExitStatus.OPTIMAL)
else:
    print("No assignment")
