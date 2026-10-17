"""Probe 7: remaining API names used in the skill."""
import mip
from mip import Model, xsum, INTEGER, BINARY, MAXIMIZE

m = Model(solver_name="CBC")
m.verbose = 0
x = m.add_var("x", lb=0, ub=3, var_type=INTEGER)
y = m.add_var("y", obj=2.0, var_type=BINARY)
c = m.add_constr(x + y <= 3, name="cap")
print("add_constr returns", type(c).__name__, c.name)
print("var types", mip.BINARY, mip.INTEGER, mip.CONTINUOUS, mip.INF)
print("var obj set via add_var:", {v.name: co for v, co in m.objective.expr.items()})
m.objective = xsum([x, y]) + 0
print("status", m.optimize(max_seconds=5).name, "obj", m.objective_value, "bound", m.objective_bound, "gap", m.gap)
print("num_solutions", m.num_solutions, "x.xi(0)", x.xi(0))
print("var_by_name", m.var_by_name("cap") is None, m.var_by_name("y").name)
print("sum builds", type(sum([x, y])).__name__)
print("v.lb/ub/var_type", x.lb, x.ub, x.var_type, y.var_type)
print("default seed", m.seed, "integer_tol", m.integer_tol)
print("num_cols", m.num_cols, "num_rows", m.num_rows)
print("threads default", m.threads, "max_mip_gap", m.max_mip_gap)
