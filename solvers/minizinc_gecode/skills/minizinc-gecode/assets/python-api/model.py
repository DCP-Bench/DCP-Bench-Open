"""Choose the cheapest set of depots that serves every district.

Shows the Python API: data passed from Python, a time limit, and a
branch for each status the solver can return.
"""
from datetime import timedelta

from minizinc import Instance, Model, Solver, Status

COVERS = [  # COVERS[district][depot] = 1 when the depot can serve the district
    [1, 0, 1, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 1],
    [0, 0, 1, 1],
]
COST = [5, 3, 4, 2]

MODEL = """
int: n_districts;
int: n_depots;
array[1..n_districts, 1..n_depots] of int: covers;
array[1..n_depots] of int: cost;
array[1..n_depots] of var bool: chosen;
var int: total;

constraint total = sum(d in 1..n_depots)(cost[d] * bool2int(chosen[d]));
constraint forall(k in 1..n_districts)(
    exists(d in 1..n_depots)(covers[k, d] = 1 /\\ chosen[d]));

solve minimize total;
"""

model = Model()
model.add_string(MODEL)
instance = Instance(Solver.lookup("gecode"), model)
instance["n_districts"] = len(COVERS)
instance["n_depots"] = len(COST)
instance["covers"] = COVERS
instance["cost"] = COST

result = instance.solve(timeout=timedelta(seconds=10))
print("status:", result.status.name)
if result.status == Status.OPTIMAL_SOLUTION:
    depots = [d + 1 for d, used in enumerate(result["chosen"]) if used]
    print("total cost:", result["total"])
    print("depots:", depots)
elif result.status == Status.SATISFIED:
    print("best found, optimality not proven; total cost:", result["total"])
else:
    print("no answer from the solver")
