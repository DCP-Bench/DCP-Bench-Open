"""Check every encoding in the skill's table: for each input tuple and each candidate output,
the linear model is feasible exactly when the mathematical relation holds (no objective, so OPTIMAL
means a feasible point exists). Run inside the image with the python entrypoint."""
import itertools
import mip
from mip import Model, OptimizationStatus, INTEGER, BINARY

R = range(0, 4)  # small domain for inputs
M_BIG = 10  # M larger than any |difference| on the domain


def solve_feasible(build, inputs, out_value):
    m = Model(solver_name="CBC")
    m.verbose = 0
    m.max_mip_gap = 0.0
    m.max_mip_gap_abs = 0.0
    xs = [m.add_var(f"x{i}", lb=0, ub=3, var_type=INTEGER) for i in range(len(inputs))]
    z = m.add_var("z", lb=-20, ub=20, var_type=INTEGER)
    for v, val in zip(xs, inputs):
        m += v == val
    m += z == out_value
    build(m, xs, z)
    status = m.optimize(max_seconds=10)
    assert status in (OptimizationStatus.OPTIMAL, OptimizationStatus.INFEASIBLE), status
    return status == OptimizationStatus.OPTIMAL


failures = []
counts = {}


def check(name, arity, outs, build, relation, dom=R):
    n = 0
    for inputs in itertools.product(dom, repeat=arity):
        for out in outs:
            got = solve_feasible(build, list(inputs), out)
            want = relation(inputs, out)
            n += 1
            if got != want:
                failures.append((name, inputs, out, got, want))
    counts[name] = n


# x != v, v = 2, x in 0..3
def b_neq(m, xs, z):
    x = xs[0]
    b = m.add_var("b", var_type=BINARY)
    m += x <= 2 - 1 + (3 - 2 + 1) * b
    m += x >= 2 + 1 - (2 + 1 - 0) * (1 - b)
check("neq", 1, [0, 1], b_neq, lambda i, o: i[0] != 2)  # z unused: fixed to 0/1 which is ignored
# z is fixed but unused: feasibility depends on x only, so compare with z-independent relation
counts.pop("neq", None)
for inputs in itertools.product(R, repeat=1):
    for out in [0, 1]:
        got = solve_feasible(b_neq, list(inputs), out)
        if got != (inputs[0] != 2):
            failures.append(("neq", inputs, out, got, inputs[0] != 2))
counts["neq"] = len(list(itertools.product(R, repeat=1))) * 2


# c = 1 iff x >= 2 (t = 2, lo = 0, hi = 3): c is a binary attached to z (z in {0,1})
def b_iff(m, xs, z):
    x = xs[0]
    m += x >= 2 - (2 - 0) * (1 - z)
    m += x <= (2 - 1) + (3 - 2 + 1) * z
check("iff_threshold", 1, [0, 1], b_iff, lambda i, o: (o == 1) == (i[0] >= 2))

# d = |a - b| maximised: d must be able to equal |a-b| (outs over -20..20 as candidate d)
def b_abs_max(m, xs, z):
    a, b = xs[0], xs[1]
    s = m.add_var("s", var_type=BINARY)
    m += z <= a - b + M_BIG * (1 - s)
    m += z <= b - a + M_BIG * s
check("abs_max_upper", 2, [0, 1, 2, 3], b_abs_max, lambda i, o: o <= abs(i[0] - i[1]))

# minimised abs: d >= a - b, d >= b - a ; exact value under minimisation
def b_abs_min(m, xs, z):
    a, b = xs[0], xs[1]
    m += z >= a - b
    m += z >= b - a
check("abs_min_lower", 2, [0, 1, 2, 3], b_abs_min, lambda i, o: o >= abs(i[0] - i[1]))

# exact min with binary s
def b_min(m, xs, z):
    x, y = xs[0], xs[1]
    s = m.add_var("s", var_type=BINARY)
    m += z <= x
    m += z <= y
    m += z >= x - M_BIG * (1 - s)
    m += z >= y - M_BIG * s
check("min_exact", 2, [0, 1, 2, 3], b_min, lambda i, o: o == min(i))

# exact max with binary s
def b_max(m, xs, z):
    x, y = xs[0], xs[1]
    s = m.add_var("s", var_type=BINARY)
    m += z >= x
    m += z >= y
    m += z <= x + M_BIG * (1 - s)
    m += z <= y + M_BIG * s
check("max_exact", 2, [0, 1, 2, 3], b_max, lambda i, o: o == max(i))

# z = p * q (binaries)
def b_and(m, xs, z):
    p, q = xs[0], xs[1]
    m += z <= p
    m += z <= q
    m += z >= p + q - 1
check("and_binaries", 2, [0, 1], b_and, lambda i, o: o == (i[0] * i[1]), dom=[0, 1])
# note: inputs here range over 0..3, binaries need 0..1: only inputs in {0,1} are meaningful
for inputs in itertools.product([0, 1], repeat=2):
    pass

# w = b * x with b binary (input 0/1) and x integer in 0..3
def b_bx(m, xs, z):
    b, x = xs[0], xs[1]
    lo, hi = 0, 3
    m += z <= hi * b
    m += z >= lo * b
    m += z <= x - lo * (1 - b)
    m += z >= x - hi * (1 - b)
check("binary_times_int", 2, [0, 1, 2, 3], b_bx, lambda i, o: o == i[0] * i[1] if i[0] in (0, 1) else False)
failures = [f for f in failures if not (f[0] == "binary_times_int" and f[1][0] not in (0, 1))]

# one of the values {1, 2, 3}: x == 1 or 2 or 3 (x in 0..3); z is free to match x only when x is in the set
def b_set(m, xs, z):
    x = xs[0]
    ps = [m.add_var(f"p{k}", var_type=BINARY) for k in (1, 2, 3)]
    m += mip.xsum(ps) == 1
    m += x == mip.xsum(k * p for k, p in zip((1, 2, 3), ps))
check("one_of_set", 1, [0], b_set, lambda i, o: i[0] in (1, 2, 3))

# alldifferent on 2 variables with values 0..3: x0 != x1 via binaries p[i][v]
def b_alldiff(m, xs, z):
    values = range(0, 4)
    p = [[m.add_var(f"p{i}_{v}", var_type=BINARY) for v in values] for i in range(2)]
    for i in range(2):
        m += mip.xsum(p[i]) == 1
        m += xs[i] == mip.xsum(v * p[i][k] for k, v in enumerate(values))
    for k in range(4):
        m += mip.xsum(p[i][k] for i in range(2)) <= 1
check("alldiff_pair", 2, [0, 1], b_alldiff, lambda i, o: i[0] != i[1] if o == 1 else i[0] == i[1] or True)
# The relation for alldifferent is on inputs only; the output z is not used, so compare both outputs equally.
failures = [f for f in failures if f[0] != "alldiff_pair"]
for inputs in itertools.product(R, repeat=2):
    got = solve_feasible(b_alldiff, list(inputs), 0)
    if got != (inputs[0] != inputs[1]):
        failures.append(("alldiff_pair", inputs, 0, got, inputs[0] != inputs[1]))
counts["alldiff_pair"] = 16

# table lookup: v = T[idx], T = [5, 7, 9, 11], idx = x in 0..3
T = [5, 7, 9, 11]
def b_table(m, xs, z):
    idx = xs[0]
    ch = [m.add_var(f"c{k}", var_type=BINARY) for k in range(4)]
    m += mip.xsum(ch) == 1
    m += idx == mip.xsum(k * ch[k] for k in range(4))
    m += z == mip.xsum(T[k] * ch[k] for k in range(4))
check("table", 1, [5, 7, 9, 11, 6], b_table, lambda i, o: o == T[i[0]])

# disjunction: x <= 1 or y >= 2 (both in 0..3), via b1 + b2 >= 1 and big-M
def b_disj(m, xs, z):
    x, y = xs[0], xs[1]
    b1 = m.add_var("b1", var_type=BINARY)
    b2 = m.add_var("b2", var_type=BINARY)
    m += x <= 1 + M_BIG * (1 - b1)
    m += 2 <= y + M_BIG * (1 - b2)
    m += b1 + b2 >= 1
check("disjunction", 2, [0], b_disj, lambda i, o: i[0] <= 1 or i[1] >= 2)

# no-overlap of two jobs with durations 2 and 3, start s0 = x, s1 = y in 0..3, H = 3 + 2 + 3
def b_overlap(m, xs, z):
    s0, s1 = xs[0], xs[1]
    d0, d1, H = 2, 3, 8
    o = m.add_var("o", var_type=BINARY)
    m += s1 >= s0 + d0 - H * (1 - o)
    m += s0 >= s1 + d1 - H * o
check("no_overlap", 2, [0], b_overlap, lambda i, o: i[1] >= i[0] + 2 or i[0] >= i[1] + 3)

# strict: x > 1 as x >= 2 ; and x < 3 as x <= 2
def b_strict(m, xs, z):
    m += xs[0] >= 1 + 1
check("strict_gt", 1, [0], b_strict, lambda i, o: i[0] > 1)

print("cases:", counts)
print("failures:", len(failures))
for f in failures[:20]:
    print("FAIL", f)
