# Multi-commodity transportation: ship several products from origins to destinations
# so that every destination receives its demand of each product, no origin ships more
# than its supply of a product, no lane carries more than its limit, and the total
# shipping cost is as small as possible.
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
    supply = instance["supply"]  # supply[i][p] = supply of product p at origin i
    demand = instance["demand"]  # demand[j][p] = demand of product p at destination j
    limit = instance["limit"]  # limit[i][j] = most that can be shipped from i to j in total
    cost = instance["cost"]  # cost[i][j][p] = cost of shipping one unit of product p from i to j
    n_origins = len(supply)
    n_destinations = len(demand)
    n_products = len(supply[0])

    # With no negative cost, shipping more than a destination demands never pays: some
    # shipment into it could be cut, which keeps supply and lane limits satisfied and
    # does not raise the cost. The optimum is therefore reached with every demand met
    # exactly. Posting that as an equality gives the solver far stronger propagation
    # than "at least"; it does not change the optimal cost, the only declared output.
    exact_demand = all(cost[i][j][p] >= 0 for i in range(n_origins)
                       for j in range(n_destinations) for p in range(n_products))

    m = Model()
    # x[i][j][p] = units of product p shipped from origin i to destination j. A lane
    # never carries more than the origin's supply of the product or the lane limit
    # (or the destination's demand, when demands are met exactly), so that is the
    # upper bound; it keeps the integer encoding small.
    x = [[[m.int(f"x_{i}_{j}_{p}", 0,
                 min(supply[i][p], limit[i][j], demand[j][p]) if exact_demand
                 else min(supply[i][p], limit[i][j]))
           for p in range(n_products)] for j in range(n_destinations)] for i in range(n_origins)]

    # supply: an origin ships at most its supply of each product
    for i in range(n_origins):
        for p in range(n_products):
            m &= (sum(x[i][j][p] for j in range(n_destinations)) <= supply[i][p])

    # demand: a destination receives at least its demand of each product
    for j in range(n_destinations):
        for p in range(n_products):
            received = sum(x[i][j][p] for i in range(n_origins))
            m &= (received == demand[j][p]) if exact_demand else (received >= demand[j][p])

    # limit: all products together on a lane stay within the lane limit
    for i in range(n_origins):
        for j in range(n_destinations):
            m &= (sum(x[i][j][p] for p in range(n_products)) <= limit[i][j])

    # Minimise the shipping cost. x >= t is the literal "at least t units are shipped",
    # so each unit shipped is one such literal and costs the unit cost. A soft clause
    # pays when its literal is false, hence the negation: the lane pays for every
    # unit it carries.
    units = []
    for i in range(n_origins):
        for j in range(n_destinations):
            for p in range(n_products):
                for t in range(1, x[i][j][p].ub + 1):
                    if cost[i][j][p] > 0:
                        units.append((cost[i][j][p], x[i][j][p] >= t))
    for weight, unit in units:
        m.obj[weight] += ~unit

    # total_cost is a declared output. Tying an integer variable to a long weighted sum
    # through hermax's integer encoding is slow, so the units above are added up as a
    # binary number with adder circuits and the bits are then tied to the variable.
    total_cost = integer_from_bits(m, sum_bits(m, units), "total_cost")

    return m, {"total_cost": total_cost}
