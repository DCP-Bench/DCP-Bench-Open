"""Product mix: whole units of three products, two machine-hour limits, maximise profit."""
import cpmpy as cp
from cpmpy.solvers.solver_interface import ExitStatus

profit = [30, 45, 20]
# hours[k][j]: hours product j needs on machine k
hours = [[2, 3, 1],
         [1, 1, 2]]
capacity = [100, 80]

units = cp.intvar(0, 50, shape=len(profit), name="units")
model = cp.Model([cp.sum(hours[k][j] * units[j] for j in range(len(profit))) <= capacity[k]
                  for k in range(len(capacity))])
model.maximize(cp.sum(p * u for p, u in zip(profit, units)))

if model.solve():
    status = model.status().exitstatus
    print("Units:", [int(u.value()) for u in units])
    print("Profit:", int(model.objective_value()))
    print("Proven optimal:", status == ExitStatus.OPTIMAL)
else:
    print("No feasible plan")
