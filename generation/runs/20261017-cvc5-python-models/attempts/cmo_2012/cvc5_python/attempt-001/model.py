# Problem cmo_2012: given two positive integers a and b, where a - b is a prime
# number and a * b is a perfect square n^2 (with b > 0), find the smallest value
# of a that is no less than the given minimum. Output a, b, n and p = a - b.
import math

import cvc5.pythonic as cz


def build(instance):
    lo = instance["min_a"]
    hi = instance["max_val"]

    a, b, n, p = cz.Ints("a b n p")
    s = cz.SolverFor("QF_NIA")

    # a and b are positive integers, a no less than the given minimum, b > 0.
    s.add(a >= lo, a <= hi, b >= 1, b <= a)
    # n is a positive integer; p is the difference a - b.
    s.add(n >= 1, n <= hi, p >= 2, p <= hi)
    s.add(p == a - b)

    # a - b is a prime number: p has no divisor d with 2 <= d < p.
    # Any composite p <= hi has a divisor d with d * d <= hi.
    for d in range(2, math.isqrt(hi) + 1):
        q, r = cz.Ints(f"q_{d} r_{d}")
        s.add(p == d * q + r, r >= 0, r < d)
        s.add(cz.Implies(p > d, r != 0))

    # a * b is a perfect square n^2.
    s.add(a * b == n * n)

    return s, {"a": a, "b": b, "n": n, "p": p}, ("minimize", a)
