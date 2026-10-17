# Problem cmo_2012: given two positive integers a and b, where a - b is a prime
# number and a * b is a perfect square n^2 (with b > 0), find the smallest value
# of a that is no less than the given minimum. Output a, b, n and p = a - b.
import math

import cvc5.pythonic as cz


def build(instance):
    lo = instance["min_a"]
    hi = instance["max_val"]
    root = math.isqrt(hi)

    a, b, n, p = cz.Ints("a b n p")
    s, t = cz.Ints("s t")
    solver = cz.Solver()

    # a and b are positive integers, a no less than the given minimum, b > 0.
    solver.add(a >= lo, a <= hi, b >= 1, b <= a)
    # n is a positive integer; p is the difference a - b.
    solver.add(n >= 1, n <= hi, p >= 2, p <= hi)
    solver.add(p == a - b)

    # a - b is a prime number: p has no divisor d with 2 <= d < p.
    # Any composite p <= hi has a divisor d with d * d <= hi.
    for d in range(2, root + 1):
        q, r = cz.Ints(f"q_{d} r_{d}")
        solver.add(p == d * q + r, r >= 0, r < d)
        solver.add(cz.Implies(p > d, r != 0))

    # a * b is a perfect square n^2. Since a - b is prime and b > 0, the square
    # root of a and of b are whole numbers: a = s^2, b = t^2 with 1 <= t < s,
    # and n = s * t. The squares are written as lookup tables over s and t, so
    # every term stays linear (cvc5 is slow on products of two unknowns).
    solver.add(s >= 2, s <= root, t >= 1, t < s)
    solver.add(a == cz.Sum([cz.If(s == k, k * k, 0) for k in range(2, root + 1)]))
    solver.add(b == cz.Sum([cz.If(t == j, j * j, 0) for j in range(1, root)]))
    solver.add(n == cz.Sum([cz.If(s == k, k * t, 0) for k in range(2, root + 1)]))

    return solver, {"a": a, "b": b, "n": n, "p": p}, ("minimize", a)
