# Circling the squares (Dudeney): place ten different numbers A..K round a circle so that
# the squares of any two adjacent numbers add up to the squares of the two numbers
# diametrically opposite them. A = 16, B = 2, F = 8 and G = 14 are given.
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


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]
    given = {"A": 16, "B": 2, "F": 8, "G": 14}
    top = 99  # "no number need contain more than two figures"

    m = Model()
    # x[name] = the number placed in square name
    x = {name: m.int(name, 1, top) for name in names}

    # every square holds a different number
    m &= m.vector([x[name] for name in names]).all_different()

    # the four numbers placed as examples stand as they are
    for name, value in given.items():
        m &= (x[name] == value)

    # sq[name] = the square of x[name], as bits (least significant first). Squaring an
    # integer variable has no direct form here, so it is a table: when x is v, the bits
    # spell v * v.
    width = (top * top).bit_length()
    sq = {}
    for name in names:
        sq[name] = m.bool_vector(f"square_{name}", width)
        for v in range(1, top + 1):
            for k in range(width):
                bit = sq[name][k] if (v * v >> k) & 1 else ~sq[name][k]
                m &= (~(x[name] == v) | bit)

    # The squares of two adjacent numbers add up to the squares of the two numbers
    # opposite them: A,B with F,G; B,C with G,H; C,D with H,I; D,E with I,K; E,F with K,A.
    # The other five pairs of adjacent squares give the same five equations.
    for a, b, c, d in [("A", "B", "F", "G"), ("B", "C", "G", "H"), ("C", "D", "H", "I"),
                       ("D", "E", "I", "K"), ("E", "F", "K", "A")]:
        left = add_bits(m, list(sq[a]), list(sq[b]))
        right = add_bits(m, list(sq[c]), list(sq[d]))
        for p, q in zip(left, right):
            m &= (~p | q)
            m &= (p | ~q)

    return m, {name: x[name] for name in names}
