"""Probe 3: exact-gap timing, feasible-but-unproven status, float noise, big-M numerics."""
import os
import random
import sys
import time
import mip
from mip import Model, xsum, OptimizationStatus, BINARY, INTEGER, CONTINUOUS, MAXIMIZE, MINIMIZE

def big_knap(seed, n=150):
    random.seed(seed)
    wts = [random.randint(10**6, 4 * 10**6) for _ in range(n)]
    vals = [random.randint(10**6, 4 * 10**6) for _ in range(n)]
    m = Model(sense=MAXIMIZE, solver_name="CBC")
    m.verbose = 0
    m.threads = 1
    bs = [m.add_var(f"b{i}", var_type=BINARY) for i in range(n)]
    m += xsum(w * b for w, b in zip(wts, bs)) <= sum(wts) // 2
    m.objective = xsum(v * b for v, b in zip(vals, bs))
    return m, bs

print("== A. feasible-but-unproven with exact gap (max_mip_gap=0, abs=0), 150 items")
for seed in (1, 2):
    m, bs = big_knap(seed)
    m.max_mip_gap = 0.0
    m.max_mip_gap_abs = 0.0
    t0 = time.time()
    s = m.optimize(max_seconds=5)
    print(f"seed {seed}: {s} elapsed {time.time() - t0:.2f} obj {m.objective_value} bound {m.objective_bound} "
          f"gap {m.gap} solutions {m.num_solutions} x0 {bs[0].x}")

print("== B. same with default gaps, 5 s")
m, bs = big_knap(2)
t0 = time.time()
s = m.optimize(max_seconds=5)
print(f"default gap: {s} elapsed {time.time() - t0:.2f} obj {m.objective_value} bound {m.objective_bound} gap {m.gap}")

print("== C. float noise in integral values")
f = Model(solver_name="CBC")
f.verbose = 0
x = f.add_var("x", lb=0, ub=100, var_type=INTEGER)
c = f.add_var("c", lb=0, ub=100, var_type=CONTINUOUS)
f += x >= 30
f += c == 0.1 * x
f.objective = x
print("opt:", f.optimize(), "x", repr(x.x), "c", repr(c.x), "round c", round(c.x))
g = Model(solver_name="CBC")
g.verbose = 0
ys = [g.add_var(f"y{i}", lb=0, ub=10, var_type=CONTINUOUS) for i in range(3)]
g += xsum(ys) == 3
g += ys[0] == 1.0 / 3.0 * 3
g.objective = ys[0]
print("third:", g.optimize(), [repr(v.x) for v in ys])

print("== D. big-M numerics: indicator with M from bounds")
h = Model(sense=MAXIMIZE, solver_name="CBC")
h.verbose = 0
hx = h.add_var("hx", lb=0, ub=10**6, var_type=INTEGER)
hb = h.add_var("hb", var_type=BINARY)
M = 10**6 + 1
h += hx <= 500 + M * (1 - hb)
h += hx >= 10 * hb
h.objective = hx + 3 * hb
print("bigM:", h.optimize(), repr(hx.x), repr(hb.x))

print("== E. the 1e-6 tolerance: a fractional-looking value after scaling")
e = Model(sense=MAXIMIZE, solver_name="CBC")
e.verbose = 0
ex = e.add_var("ex", lb=0, ub=10**7, var_type=INTEGER)
e += 1e-7 * ex <= 0.5
e.objective = ex
print("tiny coef:", e.optimize(), repr(ex.x))

print("== F. objective constant and negatives, minimise and maximise")
for sense in (MINIMIZE, MAXIMIZE):
    k = Model(sense=sense, solver_name="CBC")
    k.verbose = 0
    kx = k.add_var("kx", lb=-4, ub=2, var_type=INTEGER)
    ky = k.add_var("ky", lb=-3, ub=3, var_type=INTEGER)
    k += kx + ky >= -5
    k.objective = 2 * kx - 3 * ky + (-11)
    s = k.optimize()
    print(sense, s, "obj", k.objective_value, "x", kx.x, "y", ky.x, "objective_const", k.objective_const)

print("== G. strict inequality on integers: x < 5 written as x <= 4")
q = Model(sense=MAXIMIZE, solver_name="CBC")
q.verbose = 0
qx = q.add_var("qx", lb=0, ub=10, var_type=INTEGER)
q += qx <= 5 - 1
q.objective = qx
print("strict:", q.optimize(), repr(qx.x))

print("== H. unbounded MIP and infeasible with exact gap settings")
u = Model(sense=MAXIMIZE, solver_name="CBC")
u.verbose = 0
ux = u.add_var("ux", lb=0, ub=mip.INF, var_type=INTEGER)
u.objective = ux
print("unbounded:", u.optimize(), ux.x)
u2 = Model(sense=MINIMIZE, solver_name="CBC")
u2.verbose = 0
ux2 = u2.add_var("ux2", lb=0, ub=10, var_type=INTEGER)
u2.objective = ux2
u2 += ux2 >= 11
print("infeasible via bounds:", u2.optimize(), ux2.x)

print("== I. verbose=1 stdout check at fd level")
sys.stdout.flush()
v = Model(solver_name="CBC")
vx = v.add_var("vx", lb=0, ub=3, var_type=INTEGER)
v.objective = vx
v.verbose = 1
v.optimize()
sys.stdout.flush()
print("after verbose run")
