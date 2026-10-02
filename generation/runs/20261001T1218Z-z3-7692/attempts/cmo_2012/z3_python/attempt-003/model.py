# CMO 2012 problem: find positive integers a and b with a - b a prime p and
# a * b a perfect square n^2, with a as small as possible and at least min_a.
import z3


def build(instance):
    min_a = instance["min_a"]      # lower bound for a
    max_val = instance["max_val"]  # upper bound of the search (as in the reference)

    # Primes below max_val, by trial division (a fixed property of the integers,
    # not of the instance).
    prime_list = [k for k in range(2, max_val) if all(k % d != 0 for d in range(2, int(k ** 0.5) + 1))]

    # The unknowns are bit-vectors, because Z3's optimiser cannot handle the product of
    # two integer variables but bit-blasts a product of bit-vectors easily. They are
    # just wide enough for max_val; products are taken in twice that width, so they
    # cannot wrap round.
    width = max(max_val.bit_length(), 1)
    a_bv = z3.BitVec("a", width)
    b_bv = z3.BitVec("b", width)
    n_bv = z3.BitVec("n", width)
    p_bv = z3.BitVec("p", width)

    def const(value):
        return z3.BitVecVal(value, width)

    def wide(v):
        return z3.ZeroExt(width, v)

    solver = z3.Solver()

    # Domains, as in the reference (all values are non-negative here).
    solver.add(z3.UGE(a_bv, const(max(min_a, 0))), z3.ULE(a_bv, const(max_val)))
    solver.add(z3.UGE(b_bv, const(1)), z3.ULE(b_bv, const(max_val)))
    solver.add(z3.ULE(n_bv, const(max_val)))
    solver.add(z3.UGE(p_bv, const(2)), z3.ULE(p_bv, const(max_val)))

    # a - b is a prime number p.
    solver.add(z3.Or([p_bv == const(q) for q in prime_list]))
    solver.add(z3.UGE(a_bv, b_bv))
    solver.add(p_bv == a_bv - b_bv)

    # a * b is a perfect square n * n.
    solver.add(wide(a_bv) * wide(b_bv) == wide(n_bv) * wide(n_bv))

    # Implied constraints that narrow n. Since p >= 2 we have b < a, hence
    # b * b < a * b < a * a, so b < n < a.
    solver.add(z3.ULT(b_bv, n_bv), z3.ULT(n_bv, a_bv))

    # The declared outputs are integers: read the bit-vectors as unsigned numbers.
    a, b, n, p = (z3.BV2Int(v) for v in (a_bv, b_bv, n_bv, p_bv))

    # Find the smallest a.
    return solver, {"a": a, "b": b, "n": n, "p": p}, ("minimize", a)
