# Fibonacci even (Project Euler 2): each Fibonacci term is the sum of the previous two, starting
# 1, 1, 2, 3, 5, 8, ...; find the sum of the even-valued terms that are below four million.
#
# The terms reach about 9 million and the sum about 4.6 million, far too many values for one
# Integer (one variable per value), so every number here is a vector of bits and the arithmetic
# is ripple-carry addition written as clauses. All coefficients stay 0/1; no pseudo-Boolean
# encoding over powers of two is needed.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    # Constants of the problem as the reference states them (the instance has no fields):
    n = 35                 # terms f[1..n] are considered
    term_bound = 10 ** 7   # every term lies in 0..10**7
    limit = 4_000_000      # a term counts when it is even and below this
    sum_bound = 10 ** 8    # the sum lies in 0..10**8
    term_bits = term_bound.bit_length()  # 24 bits hold 0..10**7
    sum_bits = sum_bound.bit_length()    # 27 bits hold 0..10**8

    pool = IDPool()
    clauses = []

    # A literal fixed to false, so constants and padding are ordinary literals.
    false = pool.id("false")
    clauses.append([-false])
    true = -false

    # auxiliary literals (adder outputs, comparison steps), numbered by a counter
    counter = [0]

    def fresh():
        counter[0] += 1
        return pool.id(("aux", counter[0]))

    def and_of(lits):
        out = fresh()
        for lit in lits:
            clauses.append([-out, lit])
        clauses.append([out] + [-lit for lit in lits])
        return out

    def or_of(lits):
        out = fresh()
        for lit in lits:
            clauses.append([out, -lit])
        clauses.append([-out] + list(lits))
        return out

    def constant(value, width):
        # bits of a fixed number, least significant first
        return [true if (value >> k) & 1 else false for k in range(width)]

    def add(a, b, width):
        # a + b as `width` bits, least significant first, by ripple-carry addition. The final
        # carry is forced to 0, so the sum must fit in `width` bits.
        carry = false
        out = []
        for k in range(width):
            s, c = fresh(), fresh()
            x, y, z = a[k], b[k], carry
            # s is the parity of x, y, z
            clauses.extend([[-x, -y, -z, s], [-x, y, z, s], [x, -y, z, s], [x, y, -z, s],
                            [x, y, z, -s], [x, -y, -z, -s], [-x, y, -z, -s], [-x, -y, z, -s]])
            # c is true when at least two of x, y, z are
            clauses.extend([[-x, -y, c], [-x, -z, c], [-y, -z, c],
                            [x, y, -c], [x, z, -c], [y, z, -c]])
            out.append(s)
            carry = c
        clauses.append([-carry])
        return out

    def at_most(bits, bound):
        # the number with these bits is at most `bound`: for every bit k where `bound` has a 0,
        # setting it is only allowed when some higher bit where `bound` has a 1 is unset.
        for k in range(len(bits)):
            if not (bound >> k) & 1:
                clauses.append([-bits[k]] + [-bits[j] for j in range(k + 1, len(bits))
                                             if (bound >> j) & 1])

    def below(bits, bound):
        # a literal that is true exactly when the number with these bits is below `bound`,
        # comparing from the most significant bit down
        less, equal = false, true
        for k in reversed(range(len(bits))):
            if (bound >> k) & 1:
                less = or_of([less, and_of([equal, -bits[k]])])
                equal = and_of([equal, bits[k]])
            else:
                equal = and_of([equal, -bits[k]])
        return less

    # f[i] = the i-th Fibonacci term, as bits: f[0] = 0, f[1] = 1, f[2] = 1
    f = [constant(0, term_bits), constant(1, term_bits), constant(1, term_bits)]
    # each new term is the sum of the previous two terms, and stays within 0..10**7
    for i in range(3, n + 1):
        f.append(add(f[i - 1], f[i - 2], term_bits))
        at_most(f[i], term_bound)

    # x[i] is true exactly when f[i] is even (its lowest bit is 0) and below four million
    x = [false] + [and_of([-f[i][0], below(f[i], limit)]) for i in range(1, n + 1)]

    # the sum of the terms selected by x, accumulated one term at a time; a term that is not
    # selected contributes 0
    total = constant(0, sum_bits)
    for i in range(1, n + 1):
        selected = [and_of([x[i], bit]) for bit in f[i]] + [false] * (sum_bits - term_bits)
        total = add(total, selected, sum_bits)

    # res = that sum, within 0..10**8. It is declared through 0/1 Integers, one per bit, so the
    # runner reads it as their weighted sum; each Integer's "== 1" literal is tied to its bit.
    res_bits = [Integer(f"res{k}", 0, 1, vpool=pool) for k in range(sum_bits)]
    engine = IntegerEngine(vars=res_bits, vpool=pool)
    for bit, lit in zip(res_bits, total):
        one = bit.equals(1)
        clauses.extend([[-one, lit], [one, -lit]])
    at_most([bit.equals(1) for bit in res_bits], sum_bound)
    res = sum(2 ** k * bit for k, bit in enumerate(res_bits))

    cnf = engine.clausify()
    cnf.extend(clauses)
    return cnf, {"res": res}
