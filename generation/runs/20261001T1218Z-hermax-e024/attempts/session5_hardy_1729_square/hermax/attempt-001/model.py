# Hardy 1729 (squares): find four different numbers a, b, c, d between 1 and 100 with
# a^2 + b^2 = c^2 + d^2.
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
    bit first."""
    result = []
    carry = None
    for i in range(max(len(xs), len(ys))):
        terms = [t for t in (xs[i] if i < len(xs) else None,
                             ys[i] if i < len(ys) else None, carry) if t is not None]
        if len(terms) == 1:
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


def square(m, x, name, low, high, width):
    """Bits of x * x for an integer variable x in low..high: when x is v, the bits spell
    v * v. Squaring an integer variable has no direct form here, so it is a table."""
    bits = m.bool_vector(name, width)
    for v in range(low, high + 1):
        for k in range(width):
            m &= (~(x == v) | (bits[k] if (v * v >> k) & 1 else ~bits[k]))
    return list(bits)


def build(instance):
    # The range is fixed by the problem; the instance carries no data.
    range_min, range_max = 1, 100

    m = Model()
    a, b, c, d = (m.int(name, range_min, range_max) for name in "abcd")

    # the four numbers are different
    m &= m.vector([a, b, c, d]).all_different()

    # a^2 + b^2 = c^2 + d^2, built as binary adders over the squares and compared bit by bit
    width = (range_max * range_max).bit_length()
    left = add_bits(m, square(m, a, "a_squared", range_min, range_max, width),
                    square(m, b, "b_squared", range_min, range_max, width))
    right = add_bits(m, square(m, c, "c_squared", range_min, range_max, width),
                     square(m, d, "d_squared", range_min, range_max, width))
    for p, q in zip(left, right):
        m &= (~p | q)
        m &= (p | ~q)

    return m, {"a": a, "b": b, "c": c, "d": d}
