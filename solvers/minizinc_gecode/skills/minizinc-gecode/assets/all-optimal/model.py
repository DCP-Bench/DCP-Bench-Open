"""Assign three workers to three tasks at the lowest total cost, then list
every assignment that reaches that cost.

Gecode cannot enumerate optimal solutions directly (all_solutions on an
optimisation model is refused), so the script runs two passes: prove the
optimum, then pin the objective to it and enumerate with a satisfy solve.
"""
from minizinc import Instance, Model, Solver, Status

COST = [[4, 2, 8], [4, 3, 7], [3, 1, 6]]  # COST[worker][task]

HEADER = """
include "globals.mzn";
int: n;
array[1..n, 1..n] of int: cost;
array[1..n] of var 1..n: task;      % task[w] = the task given to worker w
var int: objective = sum(w in 1..n)(cost[w, task[w]]);
constraint all_different(task);
"""


def model(tail):
    m = Model()
    m.add_string(HEADER + tail)
    return m


gecode = Solver.lookup("gecode")

# Pass 1: find the optimum and check that it is proven.
first = Instance(gecode, model("solve minimize objective;"))
first["n"] = len(COST)
first["cost"] = COST
best = first.solve()
if best.status != Status.OPTIMAL_SOLUTION:
    raise SystemExit(f"no proven optimum: {best.status.name}")
optimum = best["objective"]
print("optimal cost:", optimum)

# Pass 2: pin the objective to the optimum and enumerate every solution.
second = Instance(gecode, model("int: best;\nconstraint objective = best;\nsolve satisfy;"))
second["n"] = len(COST)
second["cost"] = COST
second["best"] = optimum
result = second.solve(all_solutions=True)
print("optimal assignments:", len(result.solution))
for solution in result.solution:
    print("  task per worker:", solution.task)
