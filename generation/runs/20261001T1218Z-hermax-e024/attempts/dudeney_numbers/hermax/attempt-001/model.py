# Dudeney numbers: a Dudeney number is a positive integer that is a perfect cube and
# whose decimal digits add up to its cube root. Find such a number, larger than 1, with
# at most n digits.
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


def if_equal(m, gate, bits, value):
    """Post: when the literal `gate` holds, the binary number bits (least significant
    bit first, None for a bit that is always 0) equals the constant value."""
    if value >> len(bits):  # the value needs more bits than the number can ever have
        m &= ~gate
    for k, bit in enumerate(bits):
        wanted = (value >> k) & 1
        if bit is None:
            if wanted:
                m &= ~gate
        else:
            m &= (~gate | bit) if wanted else (~gate | ~bit)


def build(instance):
    n = instance["n"]  # the number has at most n digits

    # The cube root is between 1 and 9 * n (it equals the digit sum, which is at most 9 per
    # digit) and its cube has at most n digits, so it is one of these values.
    roots = [c for c in range(1, 9 * n + 1) if c ** 3 <= 10 ** n - 1]
    largest = max(c ** 3 for c in roots)

    m = Model()
    # digit[i][b] = bit b (worth 2^b) of the i-th digit of the number, counting from the left
    digit = [m.bool_vector(f"digit_{i}", 4) for i in range(n)]
    # number = the Dudeney number (the declared output). Its largest value is the cube of
    # the largest possible cube root.
    number = m.int("number", 0, largest)
    # is_root[k] = the cube root is roots[k]
    is_root = m.bool_vector("is_root", len(roots))

    # every digit is at most 9 (a 4-bit value above 9 has bit 3 and bit 2 or bit 1)
    for i in range(n):
        m &= (~digit[i][3] | ~digit[i][2])
        m &= (~digit[i][3] | ~digit[i][1])
    # the cube root is one value
    exactly_one(m, [is_root[k] for k in range(len(roots))], "root")

    # The digits make up the number: number = sum of digit[i] * 10^(n - 1 - i). Built as a
    # binary number with adder circuits over the digit bits (a product of a bit and a
    # power of ten is a constant weight). The digit sum is built the same way.
    number_bits = sum_bits(m, [(10 ** (n - 1 - i) * 2 ** b, digit[i][b]) for i in range(n) for b in range(4)])
    digit_sum_bits = sum_bits(m, [(2 ** b, digit[i][b]) for i in range(n) for b in range(4)])

    # Cube root and cube, as a table over the possible roots c (an integer variable
    # for the number has too many values to multiply out): when the cube root is c,
    # the number is c^3 (both the integer variable and the number the digits make up)
    # and the digits add up to c.
    for k, c in enumerate(roots):
        if_equal(m, is_root[k], number_bits, c ** 3)
        if_equal(m, is_root[k], digit_sum_bits, c)
        m &= (~is_root[k] | (number >= c ** 3))
        if c ** 3 < largest:
            m &= (~is_root[k] | ~(number >= c ** 3 + 1))

    # the number is larger than 1
    m &= (number >= 2)

    return m, {"number": number}
