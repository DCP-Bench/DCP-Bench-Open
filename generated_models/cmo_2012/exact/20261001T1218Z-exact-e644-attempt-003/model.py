# CMO 2012 problem: find positive integers a and b, with a at least min_a, such that a - b is a
# prime p and a * b is a perfect square n * n, minimising a.
from math import isqrt

from exact import Exact


def build(instance):
    min_a = instance["min_a"]  # smallest value allowed for a
    max_val = instance["max_val"]  # upper bound of all unknowns (as in the reference)

    # primes below max_val: the candidates for p = a - b (computed here from max_val, as the
    # reference does, with a sieve of Eratosthenes)
    is_prime = [True] * max_val
    is_prime[0:2] = [False, False]
    for i in range(2, isqrt(max_val) + 1):
        if is_prime[i]:
            for multiple in range(i * i, max_val, i):
                is_prime[multiple] = False
    primes = [i for i in range(max_val) if is_prime[i]]

    # The relation a * b = n * n, listed as a table of all triples (a, b, n) with
    # min_a <= a <= max_val and 1 <= b <= a. Exact's native multiplication of two
    # variables searches badly, but the triples are few and easy to list: two numbers have a
    # square product exactly when they have the same square-free part s, that is a = s * k^2
    # and b = s * j^2, and then n = s * k * j. Only the relation a * b = n * n is listed;
    # that a - b is prime and a is minimal are left to the solver.
    square_free = list(range(max_val + 1))  # square_free[m] = m with every square factor removed
    for d in range(2, isqrt(max_val) + 1):
        for m in range(d * d, max_val + 1, d * d):
            while square_free[m] % (d * d) == 0:
                square_free[m] //= d * d
    members = {}  # square-free part -> the numbers 1..max_val that have it, increasing
    for m in range(1, max_val + 1):
        members.setdefault(square_free[m], []).append(m)
    triples = []
    for s, group in members.items():
        for ia, a in enumerate(group):
            if a < min_a:
                continue
            k = isqrt(a // s)
            for b in group[:ia + 1]:  # b <= a, both required by the reference
                triples.append((a, b, s * k * isqrt(b // s)))

    solver = Exact()

    # the unknowns, with the reference's domains: a in min_a..max_val, b in 1..max_val
    # (b is positive), n in 0..max_val and p in 2..max_val
    solver.addVariable("a", min_a, max_val)
    solver.addVariable("b", 1, max_val)
    solver.addVariable("n", 0, max_val)
    solver.addVariable("p", 2, max_val)

    # a >= b
    solver.addConstraint([(1, "a"), (-1, "b")], True, 0)

    # a * b = n * n: exactly one listed triple (a, b, n) is chosen, and the unknowns take its values
    chosen = [f"triple_{i}" for i in range(len(triples))]
    for name in chosen:
        solver.addVariable(name, 0, 1)
    solver.addConstraint([(1, name) for name in chosen], True, 1, True, 1)
    for position, unknown in enumerate(("a", "b", "n")):
        solver.addConstraint([(triple[position], name) for triple, name in zip(triples, chosen)]
                             + [(-1, unknown)], True, 0, True, 0)

    # p = a - b
    solver.addConstraint([(1, "a"), (-1, "b"), (-1, "p")], True, 0, True, 0)

    # p is a prime. Exact has no membership constraint, so one 0/1 variable per prime says
    # whether p equals it.
    is_p = {q: f"p_is_{q}" for q in primes}
    for name in is_p.values():
        solver.addVariable(name, 0, 1)
    solver.addConstraint([(1, name) for name in is_p.values()], True, 1, True, 1)
    solver.addConstraint([(q, name) for q, name in is_p.items()] + [(-1, "p")], True, 0, True, 0)

    # Channel the chosen triple to p, so that the solver sees at once which triples are
    # allowed: p = a - b equals q exactly when the chosen triple has difference q. For a
    # difference that is not a prime (0, 1 or composite) no triple with that difference may
    # be chosen.
    by_difference = {}
    for triple, name in zip(triples, chosen):
        by_difference.setdefault(triple[0] - triple[1], []).append(name)
    for difference, names in by_difference.items():
        same_difference = [(1, name) for name in names]
        if difference in is_p:
            solver.addConstraint(same_difference + [(-1, is_p[difference])], True, 0, True, 0)
        else:
            solver.addConstraint(same_difference, False, 0, True, 0)

    # minimise a
    return solver, {"a": "a", "b": "b", "n": "n", "p": "p"}, ("minimize", [(1, "a")])
