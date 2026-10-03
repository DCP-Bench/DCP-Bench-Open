# Subset sum with repeats: a van carried bags of coins of several kinds, each kind
# holding a known number of coins. Some bags were stolen and exactly total_coins_lost
# coins went with them. Find how many bags of each kind were stolen.
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
    total = instance["total_coins_lost"]  # coins lost in all
    coin_numbers = instance["coin_numbers"]  # coin_numbers[i] = coins in one bag of kind i
    n = len(coin_numbers)

    m = Model()
    # The number of bags of kind i is written in binary: digit[i][k] is the digit worth
    # 2^k. A bag of kind i holds coin_numbers[i] coins, so no more than
    # total // coin_numbers[i] of them can have been stolen; that fixes how many digits
    # are needed. Binary digits keep the weighted sum below short however large the
    # numbers are.
    digit = []
    for i in range(n):
        most = total // coin_numbers[i]
        digit.append(m.bool_vector(f"digit_{i}", max(1, most.bit_length())))
    # bags[i] = number of bags of kind i stolen (the declared output), tied to its digits
    bags = [integer_from_bits(m, list(digit[i]), f"bags_{i}") for i in range(n)]

    # The coins in the stolen bags add up to exactly total_coins_lost. The sum of
    # coin_numbers[i] * 2^k over the digits that are on is built as a binary number
    # with adder circuits, and every bit of it must match the same bit of the total.
    # (A pseudo-Boolean equality over the whole range of the sum is the expensive shape
    # in hermax; adders keep it small.)
    terms = [(coin_numbers[i] * 2 ** k, digit[i][k])
             for i in range(n) for k in range(len(digit[i])) if coin_numbers[i] > 0]
    bits = sum_bits(m, terms)
    if total >> len(bits):  # the total needs more bits than the sum can ever have
        m &= digit[0][0] & ~digit[0][0]
    for k, bit in enumerate(bits):
        wanted = (total >> k) & 1
        if bit is None:
            if wanted:
                m &= digit[0][0] & ~digit[0][0]
        else:
            m &= bit if wanted else ~bit

    return m, {"bags": bags}
