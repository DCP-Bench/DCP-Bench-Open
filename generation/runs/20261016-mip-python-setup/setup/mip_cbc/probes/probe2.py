"""Probe 2: status semantics, gap tolerance, pools, operators, big numbers (inside the probe image)."""
import random
import time
import mip
from mip import Model, xsum, OptimizationStatus, BINARY, INTEGER, MAXIMIZE, MINIMIZE

def knap(n, seed, gap, gapabs, secs=60):
    random.seed(seed)
    vals = [random.randint(10**6, 10**7) for _ in range(n)]
    wts = [random.randint(10**5, 10**6) for _ in range(n)]
    cap = sum(wts) // 3
    k = Model(sense=MAXIMIZE, solver_name="CBC")
    k.verbose = 0
    k.max_mip_gap = gap
    k.max_mip_gap_abs = gapabs
    k.max_seconds = secs
    xs = [k.add_var(f"b{i}", var_type=BINARY) for i in range(n)]
    k += xsum(w * xi for w, xi in zip(wts, xs)) <= cap
    k.objective = xsum(v * xi for v, xi in zip(vals, xs))
    s = k.optimize()
    return k, s, xs

print("== 1. gap tolerance: OPTIMAL with a loose gap?")
for seed in range(3):
    k0, s0, _ = knap(60, seed, 0.0, 0.0)
    k1, s1, _ = knap(60, seed, 0.5, 0.0)
    print(f"seed {seed}: exact {s0} obj {k0.objective_value} bound {k0.objective_bound} gap {k0.gap} "
          f"| loose gap=0.5: {s1} obj {k1.objective_value} bound {k1.objective_bound} gap {k1.gap}")

print("== 2. timeout with incumbent: 150-item knapsack, 3 s")
random.seed(1)
n = 150
wts = [random.randint(10**6, 4 * 10**6) for _ in range(n)]
m = Model(sense=MAXIMIZE, solver_name="CBC")
m.verbose = 0
bs = [m.add_var(f"b{i}", var_type=BINARY) for i in range(n)]
m += xsum(w * b for w, b in zip(wts, bs)) <= sum(wts) // 2
m.objective = xsum(w * b for w, b in zip(wts, bs))
t0 = time.time()
s = m.optimize(max_seconds=3)
print("status", s, "elapsed", round(time.time() - t0, 2), "obj", m.objective_value, "bound", m.objective_bound,
      "gap", m.gap, "num_solutions", m.num_solutions, "x0", bs[0].x)

print("== 3. integer infeasible with feasible LP relaxation")
q = Model(solver_name="CBC")
q.verbose = 0
z = q.add_var("z", lb=0, ub=10, var_type=INTEGER)
q += 2 * z == 1
print("2z=1:", q.optimize(), "z.x", z.x)

print("== 4. solution pool on ties (4 binaries, exactly 2 chosen, no objective)")
t = Model(solver_name="CBC")
t.verbose = 0
bb = [t.add_var(f"c{i}", var_type=BINARY) for i in range(4)]
t += xsum(bb) == 2
t.objective = xsum(bb)
s = t.optimize()
print("ties:", s, "num_solutions", t.num_solutions, "obj", t.objective_value)
for i in range(t.num_solutions):
    print("  pool", i, [bb[j].xi(i) for j in range(4)], t.objective_value_i(i) if hasattr(t, "objective_value_i") else "")

print("== 5. operators")
o = Model(solver_name="CBC")
o.verbose = 0
ox = o.add_var("ox", lb=0, ub=5, var_type=INTEGER)
oy = o.add_var("oy", lb=0, ub=5, var_type=INTEGER)
for label, fn in [
    ("xsum([3,4])", lambda: xsum([3, 4])),
    ("xsum([])", lambda: xsum([])),
    ("sum of vars (python sum)", lambda: sum([ox, oy])),
    ("xsum of expr terms", lambda: xsum([2 * ox, oy, 5])),
    ("ox*oy", lambda: ox * oy),
    ("ox/2", lambda: ox / 2),
    ("ox/0", lambda: ox / 0),
    ("2 <= 3 constraint", lambda: 2 <= 3),
    ("ox <= oy", lambda: ox <= oy),
    ("ox == 3 bool", lambda: bool(ox == 3)),
]:
    try:
        r = fn()
        print(f"{label}: {type(r).__name__} {r}")
    except Exception as ex:
        print(f"{label}: raises {type(ex).__name__}: {ex}")
try:
    o += ox
    print("o += ox (no relation) accepted; objective =", o.objective)
except Exception as ex:
    print("o += ox raises", type(ex).__name__, ex)
try:
    o += 2 <= 3
    print("o += (2<=3) accepted")
except Exception as ex:
    print("o += (2<=3) raises", type(ex).__name__, ex)
try:
    o.add_constr(xsum([]) <= 0)
    print("empty constraint accepted")
except Exception as ex:
    print("empty constraint raises", type(ex).__name__, ex)

print("== 6. big numbers")
big = Model(solver_name="CBC")
big.verbose = 0
bx = big.add_var("bx", lb=0, ub=2**40, var_type=INTEGER)
big += bx * 3 == 3 * 2**39 + 3
big.objective = bx
print("big:", big.optimize(), repr(bx.x), int(round(bx.x)) == 2**39 + 1)
hb = Model(sense=MAXIMIZE, solver_name="CBC")
hb.verbose = 0
hx = hb.add_var("hx", lb=0, ub=10**9, var_type=INTEGER)
hy = hb.add_var("hy", lb=0, ub=10**9, var_type=INTEGER)
hb += 1000 * hx + 999 * hy <= 10**12 + 7
hb.objective = 1000 * hx + 999 * hy
print("coef 1e3, 1e9 ub:", hb.optimize(), repr(hx.x), repr(hy.x), repr(hb.objective_value))

print("== 7. negative-zero and rounding")
nz = Model(sense=MINIMIZE, solver_name="CBC")
nz.verbose = 0
nx = nz.add_var("nx", lb=-3, ub=3, var_type=INTEGER)
nz += nx * 1 >= -0.0
nz.objective = -1 * nx
print("nz:", nz.optimize(), repr(nx.x), int(round(nx.x)), repr(int(round(nx.x))))
zz = Model(sense=MINIMIZE, solver_name="CBC")
zz.verbose = 0
zx = zz.add_var("zx", lb=-3, ub=3, var_type=INTEGER)
zz.objective = zx
zz += zx >= -3
print("neg value min:", zz.optimize(), repr(zx.x))

print("== 8. verbose default: does CBC write to stdout?")
v = Model(solver_name="CBC")
v.add_var("vv", lb=0, ub=3, var_type=INTEGER)
v.objective = v.vars[0]
v.optimize()
print("verbose default done", v.verbose)
