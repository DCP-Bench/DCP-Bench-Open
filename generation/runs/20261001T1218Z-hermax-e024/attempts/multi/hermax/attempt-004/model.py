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


def merge_unary(m, a, b):
    """The sum of two numbers written in unary. a[i] says "the first number is at least
    i + 1" (so a is non-increasing as a vector of truth values), likewise b. The result
    c is such a list for the sum, with both directions stated, so that c[k] holds exactly
    when the sum is at least k + 1 (a totalizer)."""
    p, q = len(a), len(b)
    if p == 0:
        return list(b)
    if q == 0:
        return list(a)
    c = [m.bool() for _ in range(p + q)]
    for i in range(p + 1):
        for j in range(q + 1):
            if i + j >= 1:  # first number >= i and second >= j make the sum >= i + j
                lits = [c[i + j - 1]]
                if i > 0:
                    lits.append(~a[i - 1])
                if j > 0:
                    lits.append(~b[j - 1])
                m &= functools.reduce(operator.or_, lits)
            if i + j < p + q:  # first number <= i and second <= j keep the sum <= i + j
                lits = [~c[i + j]]
                if i < p:
                    lits.append(a[i])
                if j < q:
                    lits.append(b[j])
                m &= functools.reduce(operator.or_, lits)
    return c


def unary_total(m, numbers):
    """The sum of several numbers, each written in unary (see merge_unary), as a unary
    number, by merging them pairwise in a balanced tree."""
    numbers = [list(x) for x in numbers if len(x) > 0]
    if not numbers:
        return []
    while len(numbers) > 1:
        merged = [merge_unary(m, numbers[i], numbers[i + 1]) for i in range(0, len(numbers) - 1, 2)]
        if len(numbers) % 2:
            merged.append(numbers[-1])
        numbers = merged
    return numbers[0]


def contradiction(m):
    """Make the model unsatisfiable."""
    never = m.bool()
    m &= never
    m &= ~never


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
                 max(1, min(supply[i][p], limit[i][j], demand[j][p]) if exact_demand
                     else min(supply[i][p], limit[i][j])))
           for p in range(n_products)] for j in range(n_destinations)] for i in range(n_origins)]
    # units[i][j][p][t - 1] = the literal "at least t units are shipped" (x >= t). The
    # literals of one lane come in order (a unary number), and the sums below add such
    # numbers with totalizers, which state a sum in both directions so that a bound on
    # it is enforced as soon as the units that settle it are known.
    units = [[[[x[i][j][p] >= t for t in range(1, x[i][j][p].ub + 1)]
               for p in range(n_products)] for j in range(n_destinations)] for i in range(n_origins)]
    # a variable whose range was widened to two values (when its upper bound would be 0)
    # must stay 0
    for i in range(n_origins):
        for j in range(n_destinations):
            for p in range(n_products):
                bound = min(supply[i][p], limit[i][j], demand[j][p]) if exact_demand \
                    else min(supply[i][p], limit[i][j])
                if bound < 1:
                    m &= ~units[i][j][p][0]

    # supply: an origin ships at most its supply of each product
    for i in range(n_origins):
        for p in range(n_products):
            shipped = unary_total(m, [units[i][j][p] for j in range(n_destinations)])
            if len(shipped) > supply[i][p]:
                m &= ~shipped[supply[i][p]]

    # demand: a destination receives at least its demand of each product (exactly its
    # demand, as explained above, when no cost is negative)
    for j in range(n_destinations):
        for p in range(n_products):
            received = unary_total(m, [units[i][j][p] for i in range(n_origins)])
            if demand[j][p] > 0:
                if len(received) < demand[j][p]:
                    contradiction(m)
                else:
                    m &= received[demand[j][p] - 1]
            if exact_demand and len(received) > demand[j][p]:
                m &= ~received[demand[j][p]]

    # limit: all products together on a lane stay within the lane limit
    for i in range(n_origins):
        for j in range(n_destinations):
            carried = unary_total(m, [units[i][j][p] for p in range(n_products)])
            if len(carried) > limit[i][j]:
                m &= ~carried[limit[i][j]]

    # Minimise the shipping cost: every unit shipped costs the unit cost of its lane and
    # product. The units that cost the same are counted together as one unary number, so
    # that the soft clauses below read "at least k units shipped at cost c" in order. A
    # soft clause pays when its literal is false, so each such statement that is true pays
    # c through its negation.
    by_cost = {}
    for i in range(n_origins):
        for j in range(n_destinations):
            for p in range(n_products):
                if cost[i][j][p] > 0:
                    by_cost.setdefault(cost[i][j][p], []).append(units[i][j][p])
    counted = {c: unary_total(m, group) for c, group in by_cost.items()}
    for c, count in counted.items():
        for at_least_k in count:
            m.obj[c] += ~at_least_k

    # total_cost is a declared output. Tying an integer variable to a long weighted sum
    # through hermax's integer encoding is slow, so the statements above are added up as a
    # binary number with adder circuits and the bits are then tied to the variable.
    total_cost = integer_from_bits(
        m, sum_bits(m, [(c, lit) for c, count in counted.items() for lit in count]), "total_cost")

    return m, {"total_cost": total_cost}
