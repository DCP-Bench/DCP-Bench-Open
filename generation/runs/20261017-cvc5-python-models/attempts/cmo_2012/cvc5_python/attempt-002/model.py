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
    solver = cz.SolverFor("QF_NIA")

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

    # a * b is a perfect square n^2.
    solver.add(a * b == n * n)

    # Redundant square roots, implied by the two constraints above: a - b is
    # prime and a * b is a square, so the square-free parts of a and b are equal
    # and must divide the prime a - b; with b > 0 that part is 1, so a and b are
    # both squares, a = s^2 and b = t^2 with 1 <= t < s, and n = s * t.
    solver.add(s >= 2, s <= root + 1, t >= 1, t < s)
    solver.add(a == s * s, b == t * t, n == s * t)

    return solver, {"a": a, "b": b, "n": n, "p": p}, ("minimize", a)
