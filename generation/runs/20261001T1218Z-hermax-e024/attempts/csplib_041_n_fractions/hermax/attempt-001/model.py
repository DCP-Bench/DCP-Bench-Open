# Fractions (CSPLib 41): find nine distinct non-zero digits A..I with
# A/BC + D/EF + G/HI = 1, where BC, EF and HI are two-digit numbers.
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


def multiply(m, xs, ys):
    """Bits of the product of two binary numbers: the sum of the partial products
    x_k AND y_l, each worth 2^(k + l)."""
    terms = []
    for k, x in enumerate(xs):
        for l, y in enumerate(ys):
            if x is not None and y is not None:
                terms.append((2 ** (k + l), define(m, [x, y], lambda p, q: p & q)))
    return sum_bits(m, terms)


def same_number(m, xs, ys):
    """Post: the binary numbers xs and ys (None for an always-0 bit) are equal."""
    for k in range(max(len(xs), len(ys))):
        p = xs[k] if k < len(xs) else None
        q = ys[k] if k < len(ys) else None
        if p is None and q is None:
            continue
        if p is None:
            m &= ~q
        elif q is None:
            m &= ~p
        else:
            m &= (~p | q)
            m &= (p | ~q)


def build(instance):
    # The equation is fixed by the problem; the instance carries no data.
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]

    m = Model()
    # the digit each letter stands for, non-zero
    x = {name: m.int(name, 1, 9) for name in names}

    # the nine digits are all different
    m &= m.vector([x[name] for name in names]).all_different()

    # bits[name] = the digit as a binary number (least significant bit first). The equation
    # multiplies variables together, which is built here as binary multiplier circuits.
    bits = {}
    for name in names:
        bits[name] = m.bool_vector(f"bits_{name}", 4)
        for v in range(1, 10):
            for b in range(4):
                bit = bits[name][b] if (v >> b) & 1 else ~bits[name][b]
                m &= (~(x[name] == v) | bit)

    def two_digit(tens, units):
        """BC = 10 * B + C"""
        return sum_bits(m, [(10 * 2 ** b, bits[tens][b]) for b in range(4)]
                        + [(2 ** b, bits[units][b]) for b in range(4)])

    bc = two_digit("B", "C")
    ef = two_digit("E", "F")
    hi = two_digit("H", "I")

    # A/BC + D/EF + G/HI = 1, multiplied through by BC * EF * HI:
    # A * EF * HI + D * BC * HI + G * BC * EF = BC * EF * HI
    ef_hi = multiply(m, ef, hi)
    bc_hi = multiply(m, bc, hi)
    bc_ef = multiply(m, bc, ef)
    left = add_bits(m, add_bits(m, multiply(m, list(bits["A"]), ef_hi),
                                multiply(m, list(bits["D"]), bc_hi)),
                    multiply(m, list(bits["G"]), bc_ef))
    right = multiply(m, bc, ef_hi)
    same_number(m, left, right)

    return m, {name: x[name] for name in names}
