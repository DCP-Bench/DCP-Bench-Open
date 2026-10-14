# Revenue maximisation: choose how many units of each flight package to sell, no more
# than the demand for it, so that the seats sold on every flight leg stay within the
# seats available and the total revenue is as large as possible.
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
    available_seats = instance["available_seats"]  # available_seats[j] = seats on flight leg j
    demand = instance["demand"]  # demand[i] = estimated demand for package i
    revenue = instance["revenue"]  # revenue[i] = revenue from selling one unit of package i
    delta = instance["delta"]  # delta[i][j] = 1 if package i uses flight leg j
    n_packages = len(demand)
    n_legs = len(available_seats)

    # A package is sold at most up to its demand and at most as often as the tightest leg
    # it uses has seats for; the second limit is implied by the capacity constraints
    # and keeps the integer variables narrow.
    limit = []
    for i in range(n_packages):
        most = demand[i]
        for j in range(n_legs):
            if delta[i][j] > 0:
                most = min(most, available_seats[j] // delta[i][j])
        limit.append(max(most, 0))

    m = Model()
    # packages_to_sell[i] = units of package i sold (a range of one value would not be
    # an integer variable in hermax, so such a package gets a spare value that is ruled out)
    packages_to_sell = []
    for i in range(n_packages):
        if limit[i] > 0:
            packages_to_sell.append(m.int(f"packages_to_sell_{i}", 0, limit[i]))
        else:
            x = m.int(f"packages_to_sell_{i}", 0, 1)
            m &= ~(x >= 1)
            packages_to_sell.append(x)

    # demand: no package is sold above its demand (the variables' upper bounds are at
    # most the demands, as set above)

    # capacity: the seats used on a flight leg by the packages that use it stay within
    # the seats available on that leg
    for j in range(n_legs):
        m &= (sum(delta[i][j] * packages_to_sell[i] for i in range(n_packages)) <= available_seats[j])

    units = []
    for i in range(n_packages):
        for t in range(1, limit[i] + 1):
            units.append((revenue[i], packages_to_sell[i] >= t))

    # max_revenue is a declared output. Tying an integer variable to a long weighted sum
    # through hermax's integer encoding is slow, so the units above are added up as a
    # binary number with adder circuits and the bits are then tied to the variable.
    revenue_bits = sum_bits(m, [u for u in units if u[0] > 0])
    max_revenue = integer_from_bits(m, revenue_bits, "max_revenue")

    # Maximise the revenue, which is the binary number just built. A soft clause pays when
    # its literal is false, so each bit of the revenue that is off pays its weight 2^k.
    # Every weight is more than all the lower ones together, so the cheapest total is the
    # largest revenue. (Paying per unit sold instead gave hundreds of soft clauses with
    # different weights, which the solver found slow.)
    for k, bit in enumerate(revenue_bits):
        if bit is not None:
            m.obj[2 ** k] += bit

    return m, {"packages_to_sell": packages_to_sell, "max_revenue": max_revenue}
