"""Probe 4: find a timeout fixture that cannot be proven in time (zero or some incumbents)."""
import random
import time
from mip import Model, xsum, OptimizationStatus, BINARY, INTEGER, MAXIMIZE, MINIMIZE


def subset_sum(gap, gapabs, secs, seed=1):
    random.seed(seed)
    weights = [random.randint(10 ** 6, 4 * 10 ** 6) for _ in range(150)]
    m = Model(sense=MAXIMIZE, solver_name="CBC")
    m.verbose = 0
    m.threads = 1
    m.max_mip_gap = gap
    m.max_mip_gap_abs = gapabs
    picks = [m.add_var(f"b{i}", var_type=BINARY) for i in range(150)]
    load = xsum(w * b for w, b in zip(weights, picks))
    m += load <= sum(weights) // 2
    m.objective = load
    t0 = time.time()
    s = m.optimize(max_seconds=secs)
    return s, round(time.time() - t0, 2), m.objective_value, m.objective_bound, m.gap, m.num_solutions, picks[0].x


print("subset-sum default gap, 5 s:", subset_sum(1e-4, 1e-10, 5))
print("subset-sum exact gap, 5 s:", subset_sum(0.0, 0.0, 5))
print("subset-sum exact gap, 5 s, seed 2:", subset_sum(0.0, 0.0, 5, seed=2))


def golomb(length, marks, gap, secs):
    m = Model(sense=MINIMIZE, solver_name="CBC")
    m.verbose = 0
    m.threads = 1
    m.max_mip_gap = gap
    m.max_mip_gap_abs = 0.0
    v = [m.add_var(f"m{i}", lb=0, ub=length, var_type=INTEGER) for i in range(marks)]
    m += v[0] == 0
    for i in range(marks - 1):
        m += v[i + 1] >= v[i] + 1
    pairs = [(i, j) for i in range(marks) for j in range(i + 1, marks)]
    d = {p: m.add_var(f"d{p[0]}_{p[1]}", lb=1, ub=length, var_type=INTEGER) for p in pairs}
    for (i, j), dv in d.items():
        m += dv == v[j] - v[i]
    for s in range(len(pairs)):
        for t in range(s + 1, len(pairs)):
            u, w = d[pairs[s]], d[pairs[t]]
            o = m.add_var(f"o{s}_{t}", var_type=BINARY)
            M = length + 1
            m += u <= w - 1 + M * (1 - o)
            m += u >= w + 1 - M * o
    m.objective = v[-1]
    t0 = time.time()
    s = m.optimize(max_seconds=secs)
    return s, round(time.time() - t0, 2), m.objective_value, m.objective_bound, v[-1].x


print("golomb 11 marks, length 72, exact gap, 3 s:", golomb(72, 11, 0.0, 3))
print("golomb 8 marks, length 40, exact gap, 10 s:", golomb(40, 8, 0.0, 10))
