# Status check: three small models that show what each outcome looks like.
# 1. a model with no solution (proven infeasible), 2. a model whose objective has no bound
# (unbounded), 3. a model solved to a proven optimum, where the gap settings decide the answer.
import mip

# 1. two binaries that must sum to at least 3
m = mip.Model(solver_name="CBC")
m.verbose = 0
p = m.add_var("p", var_type=mip.BINARY)
q = m.add_var("q", var_type=mip.BINARY)
m += p + q >= 3
status = m.optimize(max_seconds=10)
print("infeasible model:", status.name, "| p.x =", p.x)

# 2. maximise an integer with no upper bound
m = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")
m.verbose = 0
t = m.add_var("t", lb=0, var_type=mip.INTEGER)
m.objective = t
status = m.optimize(max_seconds=10)
print("unbounded model:", status.name, "| t.x =", t.x)

# 3. a knapsack with exact gap settings: OPTIMAL means the optimum is proven
m = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")
m.verbose = 0
m.max_mip_gap = 0.0
m.max_mip_gap_abs = 0.0
items = [m.add_var(f"i{k}", var_type=mip.BINARY) for k in range(4)]
m += mip.xsum([3, 4, 5, 6][k] * items[k] for k in range(4)) <= 10
m.objective = mip.xsum([4, 5, 6, 7][k] * items[k] for k in range(4))
status = m.optimize(max_seconds=10)
print("knapsack:", status.name, "| value", round(m.objective_value), "| gap", m.gap)
