"""Probe 6: how far integer and sum-valued outputs drift from integers with large coefficients."""
import random
from mip import Model, xsum, BINARY, INTEGER, MAXIMIZE

worst = 0.0
nonint = 0
trials = 0
for seed in range(20):
    random.seed(seed)
    n = 60
    coef = [random.randint(10**5, 10**9) for _ in range(n)]
    m = Model(sense=MAXIMIZE, solver_name="CBC")
    m.verbose = 0
    m.max_mip_gap = 0.0
    m.max_mip_gap_abs = 0.0
    b = [m.add_var(f"b{i}", var_type=BINARY) for i in range(n)]
    z = m.add_var("z", lb=0, ub=10**12, var_type=INTEGER)
    m += z == xsum(c * bi for c, bi in zip(coef, b))
    m += xsum(b) <= 30
    m.objective = xsum(bi * (c % 7 + 1) for c, bi in zip(coef, b)) + z * 0.001
    status = m.optimize(max_seconds=20)
    trials += 1
    for v in [z] + b:
        d = abs(v.x - round(v.x))
        worst = max(worst, d)
        if d > 0:
            nonint += 1
    print(seed, status.name, repr(z.x), "sum-check", abs(z.x - sum(c * bi.x for c, bi in zip(coef, b))))
print("trials", trials, "values off integer", nonint, "worst deviation", worst)
