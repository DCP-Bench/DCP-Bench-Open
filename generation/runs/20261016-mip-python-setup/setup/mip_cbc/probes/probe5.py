"""Probe 5: objective introspection, satisfaction detection, pinning, no-goods, unconstrained outputs."""
import sys
from mip import Model, xsum, OptimizationStatus, BINARY, INTEGER, MAXIMIZE, MINIMIZE

print("== 1. objective introspection")
e = Model(solver_name="CBC")
e.verbose = 0
ex = e.add_var("ex", lb=0, ub=4, var_type=INTEGER)
ey = e.add_var("ey", lb=-2, ub=4, var_type=INTEGER)
print("no objective: expr", dict((v.name, c) for v, c in e.objective.expr.items()), "const", e.objective.const,
      "objective_const", e.objective_const)
e.objective = 0 * ex
print("0*ex objective: expr", len(e.objective.expr), "const", e.objective.const)
e.objective = xsum([2 * ex, -1 * ey]) + (-7)
print("objective with const -7: expr", {v.name: c for v, c in e.objective.expr.items()}, "const", e.objective.const,
      "objective_const", e.objective_const)
print("LinExpr.expr type", type(e.objective.expr).__name__)

print("== 2. satisfaction (no objective): status for feasible and infeasible")
s = Model(solver_name="CBC")
s.verbose = 0
sx = s.add_var("sx", var_type=BINARY)
sy = s.add_var("sy", var_type=BINARY)
s += sx + sy == 1
print("feasible, no objective:", s.optimize(), sx.x, sy.x, "objective_value", s.objective_value, "bound", s.objective_bound)
s += sx + sy == 3
print("infeasible, no objective:", s.optimize())

print("== 3. unconstrained output variable")
u = Model(solver_name="CBC")
u.verbose = 0
ux = u.add_var("ux", lb=0, ub=5, var_type=INTEGER)
uy = u.add_var("uy", lb=2, ub=5, var_type=INTEGER)
u += ux >= 1
u.objective = ux
print("uy unconstrained:", u.optimize(), repr(ux.x), repr(uy.x))

print("== 4. Var attributes")
print("lb/ub/type:", ux.lb, ux.ub, ux.var_type, uy.lb, uy.ub, uy.var_type, sx.lb, sx.ub, sx.var_type)
print("name", ux.name, "var_by_name", u.var_by_name("uy").name, "num vars", len(u.vars))

print("== 5. empty model warning stream")
z = Model(solver_name="CBC")
r = z.optimize()
print("empty model:", r)

print("== 6. enumeration by no-goods on 4 binaries, sum==2, all 6 assignments")
t = Model(solver_name="CBC")
t.verbose = 0
bs = [t.add_var(f"c{i}", var_type=BINARY) for i in range(4)]
t += xsum(bs) == 2
found = []
while True:
    st = t.optimize()
    if st != OptimizationStatus.OPTIMAL:
        print("stop:", st)
        break
    vals = [int(round(b.x)) for b in bs]
    found.append(tuple(vals))
    below_above = []
    t += xsum((1 - b) if v == 1 else b for b, v in zip(bs, vals)) >= 1
print("solutions", len(found), sorted(found))

print("== 7. pin the objective, then enumerate optima")
p = Model(sense=MAXIMIZE, solver_name="CBC")
p.verbose = 0
ps = [p.add_var(f"p{i}", var_type=BINARY) for i in range(6)]
weights = [3, 1, 2, 3, 1, 2]
p += xsum(w * b for w, b in zip(weights, ps)) <= 6
p.objective = xsum(b for b in ps)   # ties: many optima
st = p.optimize()
best = p.objective_value
print("best", st, best)
p += p.objective <= best + 1e-6
p += p.objective >= best - 1e-6
print("pinned objective expr:", {v.name: c for v, c in p.objective.expr.items()}, "const", p.objective.const)
seen = set()
while True:
    st = p.optimize()
    if st != OptimizationStatus.OPTIMAL:
        print("stop pinned:", st)
        break
    vals = tuple(int(round(b.x)) for b in ps)
    seen.add(vals)
    p += xsum((1 - b) if v == 1 else b for b, v in zip(ps, vals)) >= 1
print("optimal assignments found:", len(seen))
print("sorted", sorted(seen))

print("== 8. constant-only objective with pinning (const included?)")
c = Model(sense=MINIMIZE, solver_name="CBC")
c.verbose = 0
cx = c.add_var("cx", lb=0, ub=3, var_type=INTEGER)
c.objective = cx + 10
c += cx >= 1
print(c.optimize(), c.objective_value, cx.x)
