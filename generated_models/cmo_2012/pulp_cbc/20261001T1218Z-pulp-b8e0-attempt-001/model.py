"""CMO 2012: given two positive integers a and b, where a - b is a prime number p
and a * b is a perfect square n^2, find the smallest a that is at least min_a.

All of a, b, n, p are at most max_val, b is at least 1, and p is a prime below
max_val. The model reports a, b, n and p.
"""
import math

import pulp


def primes_below(limit):
    """The primes p with 2 <= p < limit (the reference's own list of allowed p)."""
    sieve = [True] * max(limit, 2)
    found = []
    for candidate in range(2, limit):
        if sieve[candidate]:
            found.append(candidate)
            for multiple in range(candidate * candidate, limit, candidate):
                sieve[multiple] = False
    return found


def build(instance):
    min_a = instance["min_a"]      # a must be at least this
    max_val = instance["max_val"]  # upper bound on a, b, n, p

    problem = pulp.LpProblem("cmo_2012", pulp.LpMinimize)

    a = pulp.LpVariable("a", min_a, max_val, cat="Integer")
    b = pulp.LpVariable("b", 1, max_val, cat="Integer")
    n = pulp.LpVariable("n", 0, max_val, cat="Integer")
    p = pulp.LpVariable("p", 2, max_val, cat="Integer")

    # objective: the smallest a
    problem += a

    # p is a prime below max_val: one 0/1 variable per prime, exactly one chosen
    prime_list = primes_below(max_val)
    is_p = {q: pulp.LpVariable(f"is_p_{q}", cat="Binary") for q in prime_list}
    problem += pulp.lpSum(is_p.values()) == 1
    problem += p == pulp.lpSum(q * var for q, var in is_p.items())

    # a - b = p
    problem += p == a - b

    # a * b = n^2 is not linear, so it is replaced by an equivalent description.
    # Write a = g*x and b = g*y with g = gcd(a, b); a*b = g^2*x*y is a square only if
    # x*y is, and x, y share no factor, so x = s^2 and y = t^2 with s > t >= 1
    # (a > b because p >= 2, and b >= 1). Then a - b = g*(s - t)*(s + t), and
    # s + t >= 3, so it can be prime only when g = 1, s - t = 1 and s + t = p. So
    #   a = s^2,  b = (s - 1)^2,  n = s*(s - 1),  p = 2*s - 1,
    # and every such s gives a * b = n^2 and a - b = p. s runs over 2..sqrt(max_val)
    # because a = s^2 <= max_val; one 0/1 variable per s, exactly one chosen.
    top = math.isqrt(max_val)
    is_s = {s: pulp.LpVariable(f"is_s_{s}", cat="Binary") for s in range(2, top + 1)}
    problem += pulp.lpSum(is_s.values()) == 1
    problem += a == pulp.lpSum(s * s * var for s, var in is_s.items())
    problem += b == pulp.lpSum((s - 1) ** 2 * var for s, var in is_s.items())
    problem += n == pulp.lpSum(s * (s - 1) * var for s, var in is_s.items())
    problem += p == pulp.lpSum((2 * s - 1) * var for s, var in is_s.items())

    return problem, {"a": a, "b": b, "n": n, "p": p}
