# Two subsets with equal sums: given a list of different integers A, find two disjoint,
# non-empty subsets S and T of its elements whose sums are equal. S and T together need
# not use every element.

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
    A = instance["A"]  # the given integers
    n = len(A)

    m = Model()
    # in_S[i] = element i is in S, in_T[i] = element i is in T
    in_S = m.bool_vector("in_S", n)
    in_T = m.bool_vector("in_T", n)

    # S and T are disjoint: no element is in both
    for i in range(n):
        m &= (~in_S[i] | ~in_T[i])

    # S and T are not empty
    m &= in_S.at_least_one()
    m &= in_T.at_least_one()

    # The elements of S add up to the same sum as the elements of T. Each sum is built
    # as a binary number with adder circuits over the elements chosen (a pseudo-Boolean
    # equality over the whole range of the sums is the expensive shape in hermax), and
    # the two numbers must agree bit by bit.
    sum_S = sum_bits(m, [(A[i], in_S[i]) for i in range(n) if A[i] > 0])
    sum_T = sum_bits(m, [(A[i], in_T[i]) for i in range(n) if A[i] > 0])
    equal_bits(m, sum_S, sum_T)

    return m, {"in_S": in_S, "in_T": in_T}
