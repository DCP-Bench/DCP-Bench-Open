# CMO 2012 problem: find positive integers a and b with a - b a prime p and
# a * b a perfect square n^2, with a as small as possible and at least min_a.
import z3


def build(instance):
    min_a = instance["min_a"]      # lower bound for a
    max_val = instance["max_val"]  # upper bound of the search (as in the reference)

    # Primes below max_val, by trial division (a fixed property of the integers,
    # not of the instance).
    prime_list = [k for k in range(2, max_val) if all(k % d != 0 for d in range(2, int(k ** 0.5) + 1))]

    a = z3.Int("a")
    b = z3.Int("b")
    n = z3.Int("n")
    p = z3.Int("p")

    solver = z3.Solver()

    # Domains, as in the reference.
    solver.add(a >= min_a, a <= max_val)
    solver.add(b >= 1, b <= max_val)
    solver.add(n >= 0, n <= max_val)
    solver.add(p >= 2, p <= max_val)

    # a - b is a prime number p.
    solver.add(z3.Or([p == q for q in prime_list]))
    solver.add(a >= b)
    solver.add(p == a - b)

    # a * b is a perfect square n * n.
    solver.add(a * b == n * n)

    # Find the smallest a.
    return solver, {"a": a, "b": b, "n": n, "p": p}, ("minimize", a)
