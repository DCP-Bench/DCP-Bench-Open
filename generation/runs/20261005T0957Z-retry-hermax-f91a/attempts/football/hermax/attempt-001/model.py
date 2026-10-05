# Football squad: buy players for as close to GBP 30 million as possible without
# going over, taking the required number from each position and at least eleven
# players in total. The output is the total price in GBP thousands.
import functools
import itertools
import operator

from hermax.model import Model

BUDGET = 30000  # GBP thousands, the chairman's upper limit
# The players on offer are fixed by the problem (the instance has no fields), so
# their prices in GBP thousands are mirrored here, one list per position, with the
# fewest and most players that must be bought at that position.
POSITIONS = [
    # goalkeepers: exactly 1
    ((1, 1), [730, 1280, 3880]),
    # defenders: 2 or more
    ((2, None), [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570]),
    # midfielders: 3 or more
    ((3, None), [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130]),
    # strikers: 2 or more
    ((2, None), [4460, 6470, 7780, 8390, 9500]),
]
MIN_PLAYERS = 11  # at least this many players in all


def define(m, inputs, function):
    """A new literal equal to function(*inputs) for 0/1 inputs, as clauses."""
    out = m.bool()
    for values in itertools.product((0, 1), repeat=len(inputs)):
        clause = [~lit if value else lit for lit, value in zip(inputs, values)]
        clause.append(out if function(*values) else ~out)
        m &= functools.reduce(operator.or_, clause)
    return out


def add_bits(m, xs, ys):
    """Binary sum of two numbers given as lists of literals, least significant bit
    first, built from half and full adders. None stands for a bit that is always 0."""
    result = []
    carry = None
    for i in range(max(len(xs), len(ys))):
        terms = [t for t in (xs[i] if i < len(xs) else None,
                             ys[i] if i < len(ys) else None, carry) if t is not None]
        if not terms:
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
    """Bits (least significant first) of the sum of weight * [literal]. The running
    sum is cut to the bit length of the largest value it can reach, since the bits
    above that are always 0."""
    total, high = [None], 0
    for weight, lit in terms:
        term = [lit if (weight >> k) & 1 else None for k in range(weight.bit_length())]
        total = add_bits(m, total, term)
        high += weight
        total = total[:max(1, high.bit_length())]
    return total


def gate_and(m, x, y):
    """x AND y for literals or the constants True / False."""
    if x is False or y is False:
        return False
    if x is True:
        return y
    if y is True:
        return x
    return define(m, [x, y], lambda a, b: a & b)


def gate_or(m, x, y):
    """x OR y for literals or the constants True / False."""
    if x is True or y is True:
        return True
    if x is False:
        return y
    if y is False:
        return x
    return define(m, [x, y], lambda a, b: a | b)


def comparator(m, bits):
    """at_least(t): a literal (or constant) that holds exactly when the binary number
    `bits` is at least t. Built from the top bit down and shared between values of t."""
    memo = {}

    def at_least(level, t):
        if t <= 0:
            return True
        if t >= 2 ** level:
            return False
        if (level, t) not in memo:
            top = bits[level - 1] if bits[level - 1] is not None else False
            half = 2 ** (level - 1)
            if t >= half:  # needs the top bit and enough in the rest
                memo[(level, t)] = gate_and(m, top, at_least(level - 1, t - half))
            else:  # the top bit alone is enough, or the rest is
                memo[(level, t)] = gate_or(m, top, at_least(level - 1, t))
        return memo[(level, t)]

    return lambda t: at_least(len(bits), t)


def require(m, holds):
    """Post a literal or a constant as a hard constraint."""
    if holds is False:
        raise ValueError("an implied bound is contradicted")
    if holds is not True:
        m &= holds


def build(instance):
    m = Model()
    # buy[k][j] is true when player j of position k is bought
    buy = [m.bool_vector(f"buy_{k}", len(prices)) for k, (_, prices) in enumerate(POSITIONS)]

    # the number of players bought at each position lies within its limits
    for k, ((lowest, highest), prices) in enumerate(POSITIONS):
        if lowest == highest == 1:
            m &= buy[k].exactly_one()
            continue
        m &= (sum(1 * buy[k][j] for j in range(len(prices))) >= lowest)
        if highest is not None and highest < len(prices):
            m &= (sum(1 * buy[k][j] for j in range(len(prices))) <= highest)

    # at least eleven players in total
    m &= (sum(1 * buy[k][j] for k, (_, prices) in enumerate(POSITIONS)
              for j in range(len(prices))) >= MIN_PLAYERS)

    # The total price, as a binary number added up with adder circuits: a
    # pseudo-Boolean equality between the price sum and an integer is the encoding
    # that timed out before.
    bits = sum_bits(m, [(price, buy[k][j]) for k, (_, prices) in enumerate(POSITIONS)
                        for j, price in enumerate(prices)])

    # The total price stays within the budget: no bit worth more than the budget
    # may be set, and the remaining bits compare at most equal to it.
    width = BUDGET.bit_length()
    for bit in bits[width:]:
        if bit is not None:
            m &= ~bit
    bits = bits[:width]
    at_least = comparator(m, bits)
    over = at_least(BUDGET + 1)
    require(m, (not over) if isinstance(over, bool) else ~over)

    # Lower bound on any squad's price, derived from the data: the cheapest players
    # meeting each position's minimum, then the cheapest remaining players allowed
    # until eleven are bought. Each position's cost grows convexly in the number
    # bought, so taking the cheapest additions first gives the least total.
    least = 0
    spare = []
    bought = 0
    for (lowest, highest), prices in POSITIONS:
        ordered = sorted(prices)
        cap = len(prices) if highest is None else min(highest, len(prices))
        least += sum(ordered[:lowest])
        bought += lowest
        spare += ordered[lowest:cap]
    least += sum(sorted(spare)[:max(0, MIN_PLAYERS - bought)])
    require(m, at_least(least))  # implied: every squad costs at least this

    # z = total price paid (declared output), between the derived lower bound and
    # the budget. Its order literal "z >= t" is tied to the comparison of the bits
    # with t, which keeps the integer narrow (about 1700 values).
    z = m.int("z", least, BUDGET)
    for t in range(least + 1, BUDGET + 1):
        holds = at_least(t)
        if holds is True:
            m &= (z >= t)
        elif holds is False:
            m &= ~(z >= t)
        else:
            m &= (~(z >= t) | holds)
            m &= ((z >= t) | ~holds)

    # Spend as much as possible: one unit soft clause per value t above the lower
    # bound, paid when z >= t is false, so the cost is BUDGET - z. Each step of the
    # core-guided search then refutes a single value of z from the top down.
    for t in range(least + 1, BUDGET + 1):
        m.obj[1] += (z >= t)

    return m, {"z": z}
