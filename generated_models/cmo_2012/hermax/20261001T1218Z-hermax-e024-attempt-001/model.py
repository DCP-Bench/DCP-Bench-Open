# CMO 2012 problem: find positive integers a and b such that a - b is a prime p
# and a * b is a perfect square n * n, with a no less than a given minimum and
# as small as possible.
#
# hermax has no product of two integer variables, so the numbers are also held
# as bits and the two products are built from adder circuits (clauses over
# Booleans), which is what a SAT-based solver works with natively.
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


def multiply_bits(m, xs, ys):
    """Binary product of two numbers given as lists of literals (shift and add)."""
    total = None
    for shift, y in enumerate(ys):
        row = [None] * shift + [define(m, [x, y], lambda a, b: a & b) for x in xs]
        total = row if total is None else add_bits(m, total, row)
    return total


def equal_bits(m, us, vs):
    """Require two numbers given as bit lists to be equal."""
    for i in range(max(len(us), len(vs))):
        u = us[i] if i < len(us) else None
        v = vs[i] if i < len(vs) else None
        if u is None and v is None:
            continue
        if u is None:
            m &= ~v
        elif v is None:
            m &= ~u
        else:
            m &= (~u | v)
            m &= (u | ~v)


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
    of t, so the whole link has about 2**len(bits) gates. Adding the bits as
    scaled integers instead makes every partial sum a wide integer, which is far
    larger.
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


def new_number(m, name, width):
    """An integer of `width` bits. Returns (the integer, its bit literals)."""
    bits = [m.bool() for _ in range(width)]
    return integer_from_bits(m, bits, name), bits


def build(instance):
    min_a = instance["min_a"]  # a must be at least this
    max_val = instance["max_val"]  # every number is at most this
    width = max_val.bit_length()  # bits needed for any value up to max_val

    # the primes below max_val, as the problem lists them
    is_prime = [False, False] + [True] * (max_val - 2)
    for i in range(2, max_val):
        if is_prime[i]:
            for multiple in range(i * i, max_val, i):
                is_prime[multiple] = False

    m = Model()
    a, a_bits = new_number(m, "a", width)
    b, b_bits = new_number(m, "b", width)
    n, n_bits = new_number(m, "n", width)
    p, p_bits = new_number(m, "p", width)

    # ranges of the numbers: a between min_a and max_val, b between 1 and max_val,
    # n between 0 and max_val
    m &= (a >= min_a)
    m &= (a <= max_val)
    m &= (b >= 1)
    m &= (b <= max_val)
    m &= (n <= max_val)

    # p is a prime (it is at least 2 and below max_val): every other value is ruled out
    for value in range(2 ** width):
        if value >= max_val or not is_prime[value]:
            m &= (p != value)

    # a - b = p, written as b + p = a (this also gives a >= b)
    equal_bits(m, add_bits(m, b_bits, p_bits), a_bits)

    # a * b is the perfect square n * n
    equal_bits(m, multiply_bits(m, a_bits, b_bits), multiply_bits(m, n_bits, n_bits))

    # Minimise a: bit k of a pays 2**k when it is 1. A soft clause pays when its
    # literal is false, so the literal is the negation of the bit.
    for k in range(width):
        m.obj[2 ** k] += ~a_bits[k]

    return m, {"a": a, "b": b, "n": n, "p": p}
