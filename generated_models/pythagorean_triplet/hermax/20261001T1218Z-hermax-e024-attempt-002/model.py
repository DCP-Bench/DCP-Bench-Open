# Pythagorean triplet (Project Euler 9): find natural numbers a, b, c with
# a^2 + b^2 = c^2 and a + b + c = 1000.
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


def square(m, x, name, top, width):
    """Bits of x * x for an integer variable x in 1..top: when x is v, the bits spell v * v."""
    bits = m.bool_vector(name, width)
    for v in range(1, top + 1):
        for k in range(width):
            m &= (~(x == v) | (bits[k] if (v * v >> k) & 1 else ~bits[k]))
    return list(bits)


def build(instance):
    # The equation and the total are fixed by the problem; the instance carries no data.
    total = 1000
    top = total // 2  # each number is between 1 and 500, as in the problem's own model

    m = Model()
    a = m.int("a", 1, top)
    b = m.int("b", 1, top)
    c = m.int("c", 1, top)

    # a + b + c = 1000
    m &= (a + b + c == total)

    # The squares, as bits (least significant first). Squaring an integer variable has no
    # direct form here, so it is a table: when x is v, the bits spell v * v.
    width = (top * top).bit_length()

    # a^2 + b^2 = c^2, compared bit by bit (the sum has one bit more than c^2 can use,
    # which must then be 0)
    left = add_bits(m, square(m, a, "a_squared", top, width), square(m, b, "b_squared", top, width))
    right = square(m, c, "c_squared", top, width)
    for k, bit in enumerate(left):
        if k < len(right):
            m &= (~bit | right[k])
            m &= (bit | ~right[k])
        else:
            m &= ~bit

    return m, {"a": a, "b": b, "c": c}
