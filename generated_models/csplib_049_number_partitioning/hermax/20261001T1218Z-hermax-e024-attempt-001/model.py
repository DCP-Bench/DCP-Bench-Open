# Number partitioning: split the numbers 1..n into two sets A and B of equal size, with
# the same sum of numbers and the same sum of squares. The answer lists the n / 2
# members of A and the n / 2 members of B (in any order).

def exactly_one(m, lits, name):
    """Post "exactly one of lits is true" with a ladder encoding.

    prefix[i] says that one of lits[0..i] is true; each literal sets its prefix,
    prefixes carry on, and a literal after a set prefix is forbidden. That takes
    three clauses per literal, where forbidding every pair takes a quadratic number.
    """
    if len(lits) == 1:
        m &= lits[0]
        return
    prefix = m.bool_vector(name, len(lits))
    for i, lit in enumerate(lits):
        m &= (~lit | prefix[i])
        if i + 1 < len(lits):
            m &= (~prefix[i] | prefix[i + 1])
            m &= (~lits[i + 1] | ~prefix[i])
    m &= functools.reduce(operator.or_, lits)


def equal_bits(m, xs, ys):
    """Post that two binary numbers (lists of literals, least significant bit first,
    None for a bit that is always 0) are equal."""
    for k in range(max(len(xs), len(ys))):
        x = xs[k] if k < len(xs) else None
        y = ys[k] if k < len(ys) else None
        if x is None and y is None:
            continue
        if x is None:
            m &= ~y
        elif y is None:
            m &= ~x
        else:
            m &= (~x | y)
            m &= (x | ~y)
import functools
import itertools
import operator

from hermax.model import Model


def define(m, inputs, function):
    """A new literal that equals function(*inputs) for 0/1 inputs, as clauses."""
    out = m.bool()
    for values in itertools.product((0, 1), repeat=len(inputs)):
        clause = [~lit if value else lit for lit, value in zip(inputs, values)]
        clause.append(out if function(*values) else ~out)
        m &= functools.reduce(operator.or_, clause)
    return out


def add_bits(m, xs, ys):
    """Binary sum of two numbers given as lists of literals, least significant
    bit first. An entry None stands for a bit that is always 0."""
    result = []
    carry = None
    for i in range(max(len(xs), len(ys))):
        terms = [t for t in (xs[i] if i < len(xs) else None,
                             ys[i] if i < len(ys) else None, carry) if t is not None]
        if len(terms) == 0:
            result.append(None)
            carry = None
        elif len(terms) == 1:
            result.append(terms[0])
            carry = None
        elif len(terms) == 2:
            result.append(define(m, terms, lambda a, b: a ^ b))
            carry = define(m, terms, lambda a, b: a & b)
        else:
            result.append(define(m, terms, lambda a, b, c: a ^ b ^ c))
            carry = define(m, terms, lambda a, b, c: (a & b) | (a & c) | (b & c))
    if carry is not None:
        result.append(carry)
    return result


def sum_bits(m, terms):
    """Bits (least significant first) of the sum of weight * [literal] over
    (weight, literal) pairs. The running sum is cut to the bit length of the
    largest value it can reach, since the bits above that are always false."""
    total, high = [None], 0
    for weight, lit in terms:
        term = [lit if (weight >> k) & 1 else None for k in range(weight.bit_length())]
        total = add_bits(m, total, term)
        high += weight
        total = total[:max(1, high.bit_length())]
    return total


def literal_and(m, x, y):
    """x AND y for literals or the constants True / False."""
    if x is False or y is False:
        return False
    if x is True:
        return y
    if y is True:
        return x
    return define(m, [x, y], lambda a, b: a & b)


def literal_or(m, x, y):
    """x OR y for literals or the constants True / False."""
    if x is True or y is True:
        return True
    if x is False:
        return y
    if y is False:
        return x
    return define(m, [x, y], lambda a, b: a | b)


def integer_from_bits(m, bits, name):
    """An integer variable equal to the binary number with the given bits
    (least significant first; None is a bit that is always 0).

    Its order-encoding literal (z >= t) is tied to a comparison of the bits with
    t. The comparison is built from the top bit down and shared between values
    of t, so the whole link has about 2**len(bits) gates.
    """
    width = len(bits)
    z = m.int(name, 0, 2 ** width - 1)
    memo = {}

    def at_least(level, t):
        """The number formed by the lowest `level` bits is at least t."""
        if t <= 0:
            return True
        if t >= 2 ** level:
            return False
        if (level, t) not in memo:
            top = bits[level - 1] if bits[level - 1] is not None else False
            half = 2 ** (level - 1)
            if t >= half:  # needs the top bit and enough in the rest
                memo[(level, t)] = literal_and(m, top, at_least(level - 1, t - half))
            else:  # the top bit alone is enough, or the rest is
                memo[(level, t)] = literal_or(m, top, at_least(level - 1, t))
        return memo[(level, t)]

    for t in range(1, 2 ** width):
        holds = at_least(width, t)
        if holds is True:
            m &= (z >= t)
        elif holds is False:
            m &= ~(z >= t)
        else:
            m &= (~(z >= t) | holds)
            m &= ((z >= t) | ~holds)
    return z


def build(instance):
    n = instance["n"]  # the numbers are 1..n; n is even
    half = n // 2

    m = Model()
    # slot[s][v - 1] = position s holds the number v. Positions 0..half-1 are the members
    # of A and positions half..n-1 the members of B, so the n positions together hold
    # every number 1..n once (A and B share no number).
    slot = m.bool_matrix("slot", n, n)
    # A[i], B[i] = the i-th member of A and of B (the declared outputs)
    A = [m.int(f"A_{i}", 1, n) for i in range(half)]
    B = [m.int(f"B_{i}", 1, n) for i in range(half)]
    value = A + B

    # every position holds exactly one number and every number sits in exactly one position
    for s in range(n):
        exactly_one(m, [slot[s][v] for v in range(n)], f"position_{s}")
    for v in range(n):
        exactly_one(m, [slot[s][v] for s in range(n)], f"number_{v}")
    # A and B show the number held: holding v means value >= v and not value >= v + 1
    # (comparisons outside the range 1..n are already settled)
    for s in range(n):
        for v in range(1, n + 1):
            if v > 1:
                m &= (~slot[s][v - 1] | (value[s] >= v))
            if v < n:
                m &= (~slot[s][v - 1] | ~(value[s] >= v + 1))

    # in_A[v - 1] = number v is in A, in_B[v - 1] = number v is in B. They are read off the
    # positions, so no order of the members is implied.
    in_A = m.bool_vector("in_A", n)
    in_B = m.bool_vector("in_B", n)
    for v in range(n):
        for chosen, positions in ((in_A, range(half)), (in_B, range(half, n))):
            holding = [slot[s][v] for s in positions]
            m &= (~chosen[v] | functools.reduce(operator.or_, holding))
            for lit in holding:
                m &= (~lit | chosen[v])

    # The sum of the numbers in A equals the sum of the numbers in B. Each sum is built as a
    # binary number with adder circuits and the two numbers must agree bit by bit.
    equal_bits(m, sum_bits(m, [(v, in_A[v - 1]) for v in range(1, n + 1)]),
               sum_bits(m, [(v, in_B[v - 1]) for v in range(1, n + 1)]))
    # The sum of squares of the numbers in A equals that of B.
    equal_bits(m, sum_bits(m, [(v * v, in_A[v - 1]) for v in range(1, n + 1)]),
               sum_bits(m, [(v * v, in_B[v - 1]) for v in range(1, n + 1)]))

    return m, {"A": A, "B": B}
