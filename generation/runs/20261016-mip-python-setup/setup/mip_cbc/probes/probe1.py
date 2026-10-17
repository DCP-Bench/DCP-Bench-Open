"""Probe 1: Python-MIP 2.0.0 facts used by the skill (run inside the probe image)."""
import os
import sys
import random

import mip
import cbcbox
from mip import Model, xsum, OptimizationStatus, BINARY, INTEGER, CONTINUOUS, MAXIMIZE, MINIMIZE

print("mip version", mip.__version__)
print("cbcbox file", cbcbox.__file__)
print("env solver_name", os.environ.get("solver_name"), os.environ.get("SOLVER_NAME"))

# 1. default solver selection
m = Model()
print("default Model() solver_name:", repr(m.solver_name), type(m.solver).__name__)
m2 = Model(solver_name="CBC")
print("Model(solver_name=CBC):", m2.solver_name, type(m2.solver).__name__)
print("defaults: verbose", m.verbose, "threads", m.threads, "max_seconds", m.max_seconds,
      "max_mip_gap", m.max_mip_gap, "max_mip_gap_abs", m.max_mip_gap_abs,
      "integer_tol", m.integer_tol, "infeas_tol", m.infeas_tol, "opt_tol", m.opt_tol,
      "sense", m.sense, "objective_const", m.objective_const, "round_int_vars", m.round_int_vars,
      "sol_pool_size", m.sol_pool_size, "seed", m.seed, "max_solutions", m.max_solutions,
      "max_nodes", m.max_nodes)
print("lp_method", m.lp_method, "cuts", m.cuts, "preprocess", m.preprocess, "emphasis", m.emphasis)

# 2. no variables
e = Model()
print("empty model optimize:", e.optimize())

# 3. optimal with integer float representation and objective const
p = Model(sense=MAXIMIZE, solver_name="CBC")
p.verbose = 0
x = p.add_var("x", lb=0, ub=10, var_type=INTEGER)
y = p.add_var("y", lb=-5, ub=5, var_type=INTEGER)
p += x + 2 * y <= 17.5
p.objective = xsum([3 * x, -y]) + (-7)
st = p.optimize()
print("optimal:", st, st == OptimizationStatus.OPTIMAL, repr(x.x), repr(y.x), "obj", p.objective_value,
      "const", p.objective_const, "bound", p.objective_bound, "sense", p.sense, "num_solutions", p.num_solutions)
print("x.x type", type(x.x), "x.x == 10?", x.x == 10, "float rounding", round(x.x) == x.x)

# 4. infeasible
q = Model(solver_name="CBC")
q.verbose = 0
a = q.add_var("a", var_type=BINARY)
q += a >= 2
print("infeasible:", q.optimize(), "a.x", a.x, "objective_value", q.objective_value)

# 5. unbounded
r = Model(sense=MAXIMIZE, solver_name="CBC")
r.verbose = 0
b = r.add_var("b", lb=0, ub=mip.INF, var_type=INTEGER)
r.objective = b
print("unbounded:", r.optimize(), "b.x", b.x)

# 6. time limit that leaves an incumbent (feasible) or nothing (no solution found)
gl = Model(sense=MINIMIZE, solver_name="CBC")
gl.verbose = 0
gl.max_seconds = 3
st = None
import time
t0 = time.time()
mk = [11]
# simple big Golomb-style feasibility: 11 marks, length <= 72 (optimal 72), 3 seconds only
n_marks = 11
vs = [gl.add_var(f"m{i}", lb=0, ub=72, var_type=INTEGER) for i in range(n_marks)]
gl += vs[0] == 0
for i in range(n_marks - 1):
    gl += vs[i + 1] >= vs[i] + 1
pairs = [(i, j) for i in range(n_marks) for j in range(i + 1, n_marks)]
dv = {}
for (i, j) in pairs:
    dv[(i, j)] = gl.add_var(f"d{i}_{j}", lb=1, ub=72, var_type=INTEGER)
    gl += dv[(i, j)] == vs[j] - vs[i]
for s in range(len(pairs)):
    for t in range(s + 1, len(pairs)):
        u = dv[pairs[s]]
        w = dv[pairs[t]]
        o = gl.add_var(f"o{s}_{t}", var_type=BINARY)
        gl += u <= w - 1 + 72 * (1 - o)
        gl += u >= w + 1 - 72 * o
gl.objective = vs[-1]
st = gl.optimize(max_seconds=3)
print("golomb 3s:", st, "elapsed", round(time.time() - t0, 2), "x of last mark", vs[-1].x,
      "obj", gl.objective_value, "bound", gl.objective_bound, "num_solutions", gl.num_solutions)

# 7. truthiness of comparisons and Var*Var
t = Model(solver_name="CBC")
tx = t.add_var("tx", lb=0, ub=3, var_type=INTEGER)
ty = t.add_var("ty", lb=0, ub=3, var_type=INTEGER)
cond = tx == 3
print("tx == 3 is", type(cond).__name__, "bool(tx == 3) =", bool(cond))
try:
    z = tx * ty
    print("tx*ty gave", type(z).__name__)
except Exception as ex:
    print("tx*ty raises", type(ex).__name__, ex)
try:
    z = tx * 2.5
    print("tx*2.5 ok", z)
except Exception as ex:
    print("tx*2.5 raises", ex)
try:
    print("abs(tx)", abs(tx))
except Exception as ex:
    print("abs(tx) raises", type(ex).__name__, ex)

# 8. var_by_name and names
print("var_by_name", t.var_by_name("tx"), t.var_by_name("nope"))

# 9. max_mip_gap default (CBC allowable fraction gap) can stop an optimum early
random.seed(7)
diff = 0
for trial in range(12):
    n = 40
    vals = [random.randint(10**6, 10**7) for _ in range(n)]
    wts = [random.randint(10**5, 10**6) for _ in range(n)]
    cap = sum(wts) // 3

    def solve(gap, gapabs):
        k = Model(sense=MAXIMIZE, solver_name="CBC")
        k.verbose = 0
        k.threads = 1
        k.max_mip_gap = gap
        k.max_mip_gap_abs = gapabs
        k.max_seconds = 60
        xs = [k.add_var(f"b{i}", var_type=BINARY) for i in range(n)]
        k += xsum(w * xi for w, xi in zip(wts, xs)) <= cap
        k.objective = xsum(v * xi for v, xi in zip(vals, xs))
        s = k.optimize()
        return s, k.objective_value, k.objective_bound, k.gap

    s1, o1, b1, g1 = solve(1e-4, 1e-10)
    s2, o2, b2, g2 = solve(0.0, 0.0)
    if s1 != s2 or o1 != o2:
        diff += 1
    print(f"trial {trial}: default {s1} {o1} bound {b1} gap {g1} | exact {s2} {o2} bound {b2} gap {g2}")
print("trials where default differs from exact:", diff)
