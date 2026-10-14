# Divisible by 1 through 9 (and 10): find a ten-digit number using each digit 0-9 exactly
# once, such that the number formed by its first n digits is divisible by n, for n = 1..10.
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
    # The puzzle is fixed by the problem; the instance carries no data.
    n = 10  # ten digits, 0 to 9

    m = Model()
    # digit[i] = the i-th digit of the number, from the left
    digit = m.int_vector("digit", n, 0, 9)
    # each of the digits 0 to 9 is used exactly once
    m &= digit.all_different()

    # bits[i] = digit i as a binary number (least significant bit first), for the adder
    # circuits below
    bits = [m.bool_vector(f"bits_{i}", 4) for i in range(n)]
    for i in range(n):
        for v in range(10):
            for b in range(4):
                m &= (~(digit[i] == v) | (bits[i][b] if (v >> b) & 1 else ~bits[i][b]))

    # The number formed by the first k digits is divisible by k: it equals k times some
    # quotient. Both sides are built as binary numbers; the quotient has as many bits as
    # the largest k-digit number divided by k needs.
    for k in range(1, n + 1):
        prefix = sum_bits(m, [(10 ** (k - 1 - j) * 2 ** b, bits[j][b]) for j in range(k) for b in range(4)])
        width = ((10 ** k - 1) // k).bit_length()
        quotient = m.bool_vector(f"quotient_{k}", width)
        same_number(m, prefix, sum_bits(m, [(k * 2 ** b, quotient[b]) for b in range(width)]))

    # The number itself (the declared output). Its range is that of the reference, 0 to
    # 10^10; whether an integer variable this wide can be encoded is what this tests.
    number = m.int("number", 0, 10 ** n)
    m &= (number == sum(10 ** (n - 1 - j) * digit[j] for j in range(n)))

    return m, {"number": number}
