# Tiny integer program: choose whole numbers x and y in 0..4 to maximise 3x + 2y
# under x + 2y <= 7. Prints the proven optimum.
import mip

m = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")
m.verbose = 0                        # without this CBC's log goes to stdout
m.max_mip_gap = 0.0                  # OPTIMAL means proven, not within 0.01 %
m.max_mip_gap_abs = 0.0
x = m.add_var("x", lb=0, ub=4, var_type=mip.INTEGER)
y = m.add_var("y", lb=0, ub=4, var_type=mip.INTEGER)
# the capacity constraint
m += x + 2 * y <= 7
# the objective
m.objective = 3 * x + 2 * y
if m.optimize(max_seconds=10) == mip.OptimizationStatus.OPTIMAL:
    print("Optimal:", round(x.x), round(y.x), round(m.objective_value))
