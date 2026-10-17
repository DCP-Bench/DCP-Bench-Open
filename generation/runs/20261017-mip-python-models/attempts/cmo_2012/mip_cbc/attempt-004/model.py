# Problem cmo_2012: given positive integers a and b, where a - b is a prime number p and
# a * b is a perfect square n^2, find the smallest a no less than min_a. Output a, b, n, p.

import mip


def build(instance):
    min_a = instance["min_a"]
    max_val = instance["max_val"]

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    model.max_mip_gap = 0.0
    model.max_mip_gap_abs = 0.0

    # a is no less than the given minimum and at most max_val. b, p and n stay within
    # max_val: b < a, p = a - b < a, and n^2 = a * b < max_val^2, so n < max_val.
    a = model.add_var("a", lb=min_a, ub=max_val, var_type=mip.INTEGER)
    b = model.add_var("b", lb=1, ub=max_val - 1, var_type=mip.INTEGER)
    p = model.add_var("p", lb=2, ub=max_val - 1, var_type=mip.INTEGER)
    n = model.add_var("n", lb=1, ub=max_val - 1, var_type=mip.INTEGER)

    # Binary expansions of b and n. A product of a bounded integer with a bit is
    # linearised per bit.
    bits = max(1, max_val.bit_length())
    beta = [model.add_var(f"b_bit_{k}", var_type=mip.BINARY) for k in range(bits)]
    gamma = [model.add_var(f"n_bit_{j}", var_type=mip.BINARY) for j in range(bits)]
    # b = sum of 2^k * beta_k
    model.add_constr(b == mip.xsum((2**k) * beta[k] for k in range(bits)))
    # n = sum of 2^j * gamma_j
    model.add_constr(n == mip.xsum((2**j) * gamma[j] for j in range(bits)))

    def product_terms(x, bit_vars, prefix):
        # w_k = x * bit_k, linearised exactly for 0 <= x <= max_val and a binary bit_k.
        ws = []
        for k, bit in enumerate(bit_vars):
            w = model.add_var(f"{prefix}_w_{k}", lb=0, ub=max_val, var_type=mip.INTEGER)
            model.add_constr(w <= x)
            model.add_constr(w <= max_val * bit)
            model.add_constr(w >= x - max_val * (1 - bit))
            ws.append(w)
        return ws

    # a * b = n * n, both sides written as sums over the bits of b and of n.
    ab_terms = product_terms(a, beta, "ab")
    nn_terms = product_terms(n, gamma, "nn")
    # a * b is a perfect square n^2
    model.add_constr(
        mip.xsum((2**k) * ab_terms[k] for k in range(bits))
        == mip.xsum((2**j) * nn_terms[j] for j in range(bits))
    )

    # a - b is a prime number p. The primes below max_val are a fixed table; p is
    # chosen from it with one binary per prime.
    sieve = [True] * (max_val + 1)
    primes = []
    for q in range(2, max_val):
        if sieve[q]:
            primes.append(q)
            for m in range(q * q, max_val + 1, q):
                sieve[m] = False
    prime_choice = [model.add_var(f"p_is_{q}", var_type=mip.BINARY) for q in primes]
    model.add_constr(mip.xsum(prime_choice) == 1)
    model.add_constr(p == mip.xsum(q * prime_choice[i] for i, q in enumerate(primes)))
    # a - b is p
    model.add_constr(a - b == p)

    # Implied by a * b = n^2 with 0 < b < a: the square root n lies strictly
    # between b and a.
    model.add_constr(n >= b + 1)
    model.add_constr(n <= a - 1)

    # find the smallest a
    model.objective = mip.minimize(a)

    return model, {"a": a, "b": b, "n": n, "p": p}
