# CMO 2012: find the smallest a (at least min_a) with positive integers a, b, n, p such that a - b = p is prime and a * b = n^2.
# Approach: a*b = n^2 with a, b > 0 and a - b = p prime forces a = x^2 and b = (x-1)^2 with p = 2x-1 and n = x(x-1).
# (Write a = s*u^2, b = s*v^2 with s squarefree; s divides the prime p, and s = p gives u^2 - v^2 = 1, impossible with v >= 1.
# So s = 1, and (u-v)(u+v) = p gives u - v = 1, u + v = p.) The search is then over x, which SCIP handles far better than a*b = n^2.
import math

from pyscipopt import Model, quicksum


def primes_up_to(limit):
    # sieve of Eratosthenes, used only to list the candidate values of the prime p = 2x - 1
    if limit < 2:
        return []
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if is_p[i]:
            for j in range(i * i, limit + 1, i):
                is_p[j] = False
    return [i for i in range(limit + 1) if is_p[i]]


def build(instance):
    min_a = instance["min_a"]  # a must be at least this value
    max_val = instance["max_val"]  # upper bound on a in this data
    m = Model()
    # a = x^2 >= min_a means x >= ceil(sqrt(min_a)); b = (x-1)^2 > 0 means x >= 2
    x_lo = max(2, math.isqrt(min_a - 1) + 1) if min_a >= 1 else 2
    # a = x^2 <= max_val means x <= isqrt(max_val)
    x_hi = math.isqrt(max_val)
    x = m.addVar(name="x", vtype="I", lb=x_lo, ub=x_hi)

    # p = 2x - 1 must be prime: one binary per odd prime q = 2x - 1 in range, exactly one chosen
    candidates = [q for q in primes_up_to(2 * x_hi - 1) if q >= 2 * x_lo - 1 and q % 2 == 1]
    z = {q: m.addVar(name=f"prime_{q}", vtype="B") for q in candidates}
    # exactly one prime is chosen
    m.addCons(quicksum(z.values()) == 1)
    # x is the value that makes 2x - 1 the chosen prime
    m.addCons(x == quicksum(((q + 1) // 2) * z[q] for q in candidates))

    # minimise x, which minimises a = x^2 (increasing in x)
    m.setObjective(x, "minimize")
    # outputs: a = x^2, b = (x-1)^2, n = x(x-1), p = 2x - 1
    a = x * x
    b = (x - 1) * (x - 1)
    n = x * (x - 1)
    p = 2 * x - 1
    return m, {"a": a, "b": b, "n": n, "p": p}
