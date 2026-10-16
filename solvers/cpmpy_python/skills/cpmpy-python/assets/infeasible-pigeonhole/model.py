"""Four pigeons in three holes, one pigeon per hole: no solution exists."""
import cpmpy as cp
from cpmpy.solvers.solver_interface import ExitStatus

pigeons, holes = 4, 3
hole = cp.intvar(0, holes - 1, shape=pigeons, name="hole")  # hole of each pigeon
model = cp.Model(cp.AllDifferent(hole))

if model.solve():
    print("Solution:", [int(h.value()) for h in hole])
else:
    # solve() is False only when the status is a proof; read it rather than assume the cause.
    status = model.status().exitstatus
    print("Status:", status.name)
    print("Infeasible:", status == ExitStatus.UNSATISFIABLE)
