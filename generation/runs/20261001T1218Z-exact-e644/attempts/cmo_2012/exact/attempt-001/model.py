# CMO 2012 problem: find positive integers a and b, with a at least min_a, such that a - b is a
# prime p and a * b is a perfect square n * n, minimising a.
from exact import Exact


def build(instance):
    min_a = instance["min_a"]  # smallest value allowed for a
    max_val = instance["max_val"]  # upper bound of all unknowns (as in the reference)

    # primes below max_val: the candidates for p = a - b (computed here from max_val, as the
    # reference does, with a sieve of Eratosthenes)
    is_prime = [True] * max_val
    is_prime[0:2] = [False, False]
    for i in range(2, int(max_val ** 0.5) + 1):
        if is_prime[i]:
            for multiple in range(i * i, max_val, i):
                is_prime[multiple] = False
    primes = [i for i in range(max_val) if is_prime[i]]

    solver = Exact()

    # the unknowns, with the reference's domains: a in min_a..max_val, b in 1..max_val
    # (b is positive), n in 0..max_val and p in 2..max_val
    solver.addVariable("a", min_a, max_val)
    solver.addVariable("b", 1, max_val)
    solver.addVariable("n", 0, max_val)
    solver.addVariable("p", 2, max_val)

    # p is a prime. Exact has no membership constraint, so one 0/1 variable per prime says
    # whether p equals it (there are only a few hundred to a thousand of them).
    chosen = [f"p_is_{q}" for q in primes]
    for name in chosen:
        solver.addVariable(name, 0, 1)
    solver.addConstraint([(1, name) for name in chosen], True, 1, True, 1)
    solver.addConstraint([(q, name) for q, name in zip(primes, chosen)] + [(-1, "p")], True, 0, True, 0)

    # a is at least b, and a - b is the prime p
    solver.addConstraint([(1, "a"), (-1, "b")], True, 0)
    solver.addConstraint([(1, "a"), (-1, "b"), (-1, "p")], True, 0, True, 0)

    # a * b is the perfect square n * n: both products are given the same variable as upper
    # and lower bound, which makes them equal (Exact's addMultiplication bounds a product
    # by variable names). The product is at most max_val * max_val.
    solver.addVariable("square", 0, max_val * max_val)
    solver.addMultiplication(["a", "b"], True, "square", True, "square")
    solver.addMultiplication(["n", "n"], True, "square", True, "square")

    # minimise a
    return solver, {"a": "a", "b": "b", "n": "n", "p": "p"}, ("minimize", [(1, "a")])
