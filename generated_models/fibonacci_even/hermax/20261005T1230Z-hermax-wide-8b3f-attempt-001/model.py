# Even Fibonacci numbers (Project Euler 2): the sum of the even-valued terms of the
# Fibonacci sequence that do not exceed four million.
import functools
import itertools
import operator

from hermax.model import Model


# The terms reach about 9.2 million and the sum about 4.6 million. An IntVar over either range
# does not fit in 2048 MB in hermax, so every number here is a vector of literals (least
# significant bit first) and the arithmetic is written as clauses.


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
    bit first (a ripple-carry adder). An entry None stands for a bit that is always 0."""
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


def below(m, true, bits, bound):
    """A literal that holds exactly when the binary number bits (least significant first,
    None for an always-0 bit) is below the constant bound. Built from the lowest bit up:
    the prefix is below when its top bit is under the bound's, or equal and the rest below."""
    if bound >> len(bits):
        return true
    lt = ~true  # an empty prefix is not below anything
    for k, bit in enumerate(bits):
        bit = bit if bit is not None else ~true
        if (bound >> k) & 1:
            lt = define(m, [bit, lt], lambda b, l: (1 - b) | l)
        else:
            lt = define(m, [bit, lt], lambda b, l: (1 - b) & l)
    return lt


def build(instance):
    # The sequence length and the limit are fixed by the problem; the instance has no fields.
    n = 35            # terms f[1..35], as in the problem's own model
    limit = 4000000   # a term counts only when it is below four million
    width = 24        # f[35] = 9227465 < 2**24, so 24 bits hold every term

    m = Model()
    true = m.bool("true")
    m &= true

    # f[0] = 0, f[1] = f[2] = 1, and each later term is the sum of the previous two
    one = [true] + [None] * (width - 1)
    f = [[None] * width, one, one]
    for i in range(3, n + 1):
        f.append(add_bits(m, f[i - 1], f[i - 2])[:width])

    # x[i] = f[i] is even and below four million (x[0] is false)
    x = [~true]
    for i in range(1, n + 1):
        even = ~f[i][0] if f[i][0] is not None else true
        x.append(define(m, [even, below(m, true, f[i], limit)], lambda e, b: e & b))

    # res = the sum of x[i] * f[i]: each term is masked by x[i] and added to the running total
    total = [None]
    for i in range(1, n + 1):
        masked = [define(m, [x[i], bit], lambda s, b: s & b) if bit is not None else None
                  for bit in f[i]]
        total = add_bits(m, total, masked)

    # The declared output is the total read as a binary number.
    res = sum(2 ** k * bit for k, bit in enumerate(total) if bit is not None)

    return m, {"res": res}
