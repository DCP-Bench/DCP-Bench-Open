"""Four pigeons, three holes, at most one pigeon per hole: no solution."""
from pycsp3 import *

hole = VarArray(size=4, dom=range(3))

satisfy(
    # no two pigeons share a hole
    AllDifferent(hole),
)

status = solve()
if status is UNSAT:
    print("Infeasible: proven, no solution exists")
elif status is SAT:
    print("Solution:", values(hole))
else:
    print("Unknown: no answer within the limits (or a solver error, see the solver_*.log file)")
