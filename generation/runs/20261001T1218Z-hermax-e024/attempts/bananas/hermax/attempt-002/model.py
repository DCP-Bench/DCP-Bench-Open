# Bananas: buy 100 fruits for 100 dollars, where five bananas cost 3 dollars, seven
# oranges 5 dollars, nine mangoes 7 dollars and three apples 9 dollars. Every kind
# must be bought, and as few bananas and apples as possible.
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


def fix_value(m, bits, value):
    """Post: the binary number bits (least significant first, None for an always-0
    bit) equals the constant value."""
    assert value >> len(bits) == 0, "the value cannot be reached"
    for k, bit in enumerate(bits):
        wanted = (value >> k) & 1
        if bit is None:
            assert not wanted, "the value cannot be reached"
        else:
            m &= bit if wanted else ~bit


def build(instance):
    # The prices and totals are fixed by the problem; the instance carries no data.
    fruits = 100
    dollars = 100
    names = ["bananas", "oranges", "mangoes", "apples"]
    # price per fruit as (dollars, fruits): 3/5, 5/7, 7/9, 9/3
    price = {"bananas": (3, 5), "oranges": (5, 7), "mangoes": (7, 9), "apples": (9, 3)}

    m = Model()
    width = fruits.bit_length()
    # count[f] = how many of fruit f to buy, at least one of every kind, at most all 100
    count = {f: m.int(f, 1, fruits) for f in names}
    # bits[f][k] = bit k (worth 2^k) of count[f]. The sums below are built from these bits
    # with adder circuits, because the cost equation, posted as a linear equality over the
    # integer variables, did not finish encoding within the time limit.
    bits = {f: m.bool_vector(f"{f}_bits", width) for f in names}
    for f in names:
        # count[f] = v exactly when its bits spell v
        for v in range(1, fruits + 1):
            pattern = [bits[f][k] if (v >> k) & 1 else ~bits[f][k] for k in range(width)]
            for lit in pattern:
                m &= (~(count[f] == v) | lit)
            m &= functools.reduce(operator.or_, [~lit for lit in pattern] + [count[f] == v])

    # 100 fruits in all
    fix_value(m, sum_bits(m, [(2 ** k, bits[f][k]) for f in names for k in range(width)]), fruits)

    # They cost 100 dollars. Multiplied through by the common denominator 5 * 7 * 9 * 3 = 945
    # to clear the fractions: each fruit then costs dollars * 945 / fruits.
    scale = 1
    for f in names:
        scale *= price[f][1]
    fix_value(m, sum_bits(m, [(price[f][0] * scale // price[f][1] * 2 ** k, bits[f][k])
                              for f in names for k in range(width)]), dollars * scale)

    # Minimise bananas + apples. A soft clause pays its weight when its literal is false,
    # so the literal "bit k is off" pays 2^k whenever bit k is on: the total paid is
    # bananas + apples.
    for f in ("bananas", "apples"):
        for k in range(width):
            m.obj[2 ** k] += ~bits[f][k]

    return m, {f: count[f] for f in names}
