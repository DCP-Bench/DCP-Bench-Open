"""Brute-force the encodings in the docplex skill over small domains, and measure what each costs."""
import itertools
from docplex.mp.model import Model

fails = []


def expect(name, cond):
    if not cond:
        fails.append(name)


def fresh():
    m = Model()
    m.parameters.threads = 1
    m.parameters.mip.tolerances.mipgap = 0
    return m


def feasible(m):
    return m.solve() is not None


def cost(label, build):
    m = fresh()
    before_v, before_c = None, None
    base = build(m, measure=True)
    print(f"{label}: +{m.number_of_variables - base[0]} variables, +{m.number_of_constraints - base[1]} constraints")


U = 3
# != is native
for av, bv in itertools.product(range(U + 1), repeat=2):
    m = fresh(); a = m.integer_var(0, U); b = m.integer_var(0, U)
    m.add(a != b); m.add(a == av); m.add(b == bv)
    expect(f"neq {av},{bv}", feasible(m) == (av != bv))
# abs of an expression
for av, bv in itertools.product(range(U + 1), repeat=2):
    m = fresh(); a = m.integer_var(0, U); b = m.integer_var(0, U); d = m.integer_var(0, U)
    m.add(d == m.abs(a - b)); m.add(a == av); m.add(b == bv)
    s = m.solve(); expect(f"abs {av},{bv}", s is not None and round(s[d]) == abs(av - bv))
# reified equality through add_equivalence
for av, bv, cv in itertools.product(range(U + 1), range(U + 1), (0, 1)):
    m = fresh(); a = m.integer_var(0, U); b = m.integer_var(0, U); c = m.binary_var()
    m.add_equivalence(c, a == b); m.add(a == av); m.add(b == bv); m.add(c == cv)
    expect(f"reif {av},{bv},{cv}", feasible(m) == ((av == bv) == (cv == 1)))
# disjunction through indicators
for xv in range(5):
    m = fresh(); x = m.integer_var(0, 4); branch = m.binary_var_list(2)
    m.add_indicator(branch[0], x <= 1); m.add_indicator(branch[1], x >= 3); m.add(m.sum(branch) >= 1)
    m.add(x == xv)
    expect(f"disj {xv}", feasible(m) == (xv <= 1 or xv >= 3))
# if-then
for xv, yv in itertools.product(range(5), range(3)):
    m = fresh(); x = m.integer_var(0, 4); y = m.integer_var(0, 2)
    m.add_if_then(x >= 3, y == 0); m.add(x == xv); m.add(y == yv)
    expect(f"ifthen {xv},{yv}", feasible(m) == (not (xv >= 3) or yv == 0))
# all-different through an assignment matrix: 6 solutions for 3 over 1..3
m = fresh(); pick = m.binary_var_matrix(range(3), range(1, 4))
for i in range(3):
    m.add(m.sum(pick[i, v] for v in range(1, 4)) == 1)
for v in range(1, 4):
    m.add(m.sum(pick[i, v] for i in range(3)) <= 1)
x = [m.sum(v * pick[i, v] for v in range(1, 4)) for i in range(3)]
found = set()
while True:
    s = m.solve()
    if s is None:
        break
    t = tuple(round(s.get_value(e)) for e in x); found.add(t)
    m.add(m.sum(pick[i, t[i]] for i in range(3)) <= 2)
expect("alldiff count", len(found) == 6 and all(len(set(t)) == 3 for t in found))
# element
table = [5, 7, 2, 9]
for iv in range(4):
    m = fresh(); index = m.integer_var(0, 3); value = m.integer_var(0, 10); choose = m.binary_var_list(4)
    m.add(m.sum(choose) == 1); m.add(index == m.sum(j * choose[j] for j in range(4)))
    m.add(value == m.sum(table[j] * choose[j] for j in range(4))); m.add(index == iv)
    s = m.solve(); expect(f"element {iv}", s is not None and round(s[value]) == table[iv])
# binary times bounded integer, linearly
lo, hi = -2, 3
for bv, av in itertools.product((0, 1), range(lo, hi + 1)):
    m = fresh(); b = m.binary_var(); a = m.integer_var(lo, hi); p = m.integer_var(min(lo, 0), max(hi, 0))
    m.add(p <= hi * b); m.add(p >= lo * b); m.add(p <= a - lo * (1 - b)); m.add(p >= a - hi * (1 - b))
    m.add(a == av); m.add(b == bv)
    s = m.solve(); expect(f"product {bv},{av}", s is not None and round(s[p]) == bv * av)
# division and remainder
k, top = 3, 10
for av in range(top + 1):
    m = fresh(); a = m.integer_var(0, top); q = m.integer_var(0, top // k); r = m.integer_var(0, k - 1)
    m.add(a == k * q + r); m.add(a == av)
    s = m.solve(); expect(f"divmod {av}", s is not None and (round(s[q]), round(s[r])) == divmod(av, k))
# max, min, logical and/or
for av, bv in itertools.product(range(-2, 3), repeat=2):
    m = fresh(); a = m.integer_var(-2, 2); b = m.integer_var(-2, 2); y = m.integer_var(-5, 5); z = m.integer_var(-5, 5)
    m.add(y == m.max(a, b, 0)); m.add(z == m.min(a, b)); m.add(a == av); m.add(b == bv)
    s = m.solve(); expect(f"maxmin {av},{bv}", s is not None and round(s[y]) == max(av, bv, 0) and round(s[z]) == min(av, bv))
for av, bv in itertools.product((0, 1), repeat=2):
    m = fresh(); a = m.binary_var(); b = m.binary_var(); z = m.binary_var(); o = m.binary_var()
    m.add(z == m.logical_and(a, b)); m.add(o == m.logical_or(a, b)); m.add(a == av); m.add(b == bv)
    s = m.solve(); expect(f"andor {av},{bv}", s is not None and round(s[z]) == (av and bv) and round(s[o]) == (av or bv))
# lb defaults to 0 for integer_var
m = fresh(); w = m.integer_var(); expect("lb default 0", w.lb == 0)

# What each helper costs against the 1000/1000 limits, on two integer variables in 0..9.
def measured(label, post):
    m = fresh(); a = m.integer_var(0, 9); b = m.integer_var(0, 9)
    v0, c0 = m.number_of_variables, m.number_of_constraints
    post(m, a, b)
    m.solve()
    print(f"{label}: +{m.number_of_variables - v0} variables, +{m.number_of_constraints - c0} constraints"
          f" (as counted before solve by docplex)")

measured("a != b", lambda m, a, b: m.add(a != b))
measured("d == abs(a - b)", lambda m, a, b: m.add(m.integer_var(0, 9) == m.abs(a - b)))
measured("y == max(a, b)", lambda m, a, b: m.add(m.integer_var(0, 9) == m.max(a, b)))
measured("add_equivalence(c, a == b)", lambda m, a, b: m.add_equivalence(m.binary_var(), a == b))
measured("add_indicator(c, a <= b)", lambda m, a, b: m.add_indicator(m.binary_var(), a <= b))
measured("add_if_then(a >= 3, b == 0)", lambda m, a, b: m.add_if_then(a >= 3, b == 0))
print("FAILED:", fails if fails else "none")
