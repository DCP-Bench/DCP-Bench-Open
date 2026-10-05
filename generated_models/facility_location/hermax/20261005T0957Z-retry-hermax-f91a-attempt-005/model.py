# Facility location: decide which of four candidate warehouses to open and how
# many units each ships to each region, meeting every region's demand at the
# least total cost (fixed cost of the open warehouses plus shipping cost),
# subject to three rules about which warehouses may be open together.
import functools
import itertools
import operator

from hermax.model import Model

# lengths of the shipment cycles checked by the dominance rule in build
CYCLE_LENGTHS = (2,)


def define(m, inputs, function):
    """A new literal equal to function(*inputs) for 0/1 inputs, as clauses."""
    out = m.bool()
    for values in itertools.product((0, 1), repeat=len(inputs)):
        clause = [~lit if value else lit for lit, value in zip(inputs, values)]
        clause.append(out if function(*values) else ~out)
        m &= functools.reduce(operator.or_, clause)
    return out


def define_or(m, lits):
    """A new literal equal to the disjunction of several literals."""
    if len(lits) == 1:
        return lits[0]
    out = m.bool()
    m &= functools.reduce(operator.or_, [~out] + list(lits))
    for lit in lits:
        m &= (~lit | out)
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


def unary_to_bits(m, ladder):
    """Binary digits of a number 0..D given in unary, ladder[k - 1] = "at least k".
    Digit b is set on the runs of values whose b-th bit is 1; each run [s, e] is
    "at least s and not at least e + 1"."""
    top = len(ladder)

    def at_least(k):
        if k <= 0:
            return True
        if k > top:
            return False
        return ladder[k - 1]

    bits = []
    for b in range(top.bit_length()):
        runs = []
        for s in range(2 ** b, top + 1, 2 ** (b + 1)):
            e = min(s + 2 ** b - 1, top)
            low, high = at_least(s), at_least(e + 1)
            if high is False:
                runs.append(low)
            else:
                runs.append(define(m, [low, high], lambda a, c: a & (1 - c)))
        bits.append(define_or(m, runs))
    return bits


def merge_unary(m, a, b, limit):
    """Totalizer node: the sum of two unary numbers (a[i] = "first is at least i + 1",
    likewise b) as a unary number c, stated in both directions, so c[k] holds exactly
    when the sum is at least k + 1. Only the first `limit` digits are kept."""
    p, q = len(a), len(b)
    if p == 0:
        return list(b[:limit])
    if q == 0:
        return list(a[:limit])
    size = min(p + q, limit)
    c = [m.bool() for _ in range(size)]
    for i in range(min(p, size) + 1):
        for j in range(min(q, size - i) + 1):
            s = i + j
            if s >= 1:  # first >= i and second >= j make the sum >= i + j
                lits = [c[s - 1]]
                if i > 0:
                    lits.append(~a[i - 1])
                if j > 0:
                    lits.append(~b[j - 1])
                m &= functools.reduce(operator.or_, lits)
            if s < size:  # first <= i and second <= j keep the sum <= i + j
                lits = [~c[s]]
                if i < p:
                    lits.append(a[i])
                if j < q:
                    lits.append(b[j])
                m &= functools.reduce(operator.or_, lits)
    return c


def unary_total(m, numbers, limit):
    """Sum of several unary numbers as a unary number of at most `limit` digits,
    merged pairwise in a balanced tree."""
    numbers = [list(x) for x in numbers if len(x) > 0]
    if not numbers:
        return []
    while len(numbers) > 1:
        merged = [merge_unary(m, numbers[i], numbers[i + 1], limit)
                  for i in range(0, len(numbers) - 1, 2)]
        if len(numbers) % 2:
            merged.append(numbers[-1])
        numbers = merged
    return numbers[0][:limit]


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


def integer_from_bits(m, bits, lb, ub, name):
    """An integer variable over lb..ub equal to the binary number `bits`, for a
    number known to lie in lb..ub. Its order literal "x >= t" is tied to a
    comparison of the bits with t, built from the top bit down and shared."""
    memo = {}

    def at_least(level, t):
        if t <= 0:
            return True
        if t >= 2 ** level:
            return False
        if (level, t) not in memo:
            top = bits[level - 1] if bits[level - 1] is not None else False
            half = 2 ** (level - 1)
            if t >= half:
                memo[(level, t)] = gate_and(m, top, at_least(level - 1, t - half))
            else:
                memo[(level, t)] = gate_or(m, top, at_least(level - 1, t))
        return memo[(level, t)]

    width = len(bits)
    for holds, wanted in ((at_least(width, lb), True), (at_least(width, ub + 1), False)):
        if isinstance(holds, bool):
            if holds != wanted:
                raise ValueError("an implied bound on the total is contradicted")
        else:
            m &= holds if wanted else ~holds
    x = m.int(name, lb, ub)
    for t in range(lb + 1, ub + 1):
        holds = at_least(width, t)
        if holds is True:
            m &= (x >= t)
        elif holds is False:
            m &= ~(x >= t)
        else:
            m &= (~(x >= t) | holds)
            m &= ((x >= t) | ~holds)
    return x


def build(instance):
    names = instance["warehouse_s"]  # warehouse cities
    fixed_costs = instance["fixed_costs"]  # weekly fixed cost of each warehouse
    max_shipping = instance["max_shipping"]  # most units one warehouse can send per week
    demands = instance["demands"]  # weekly demand of each region
    costs = instance["shipping_costs"]  # cost per unit from warehouse i to region j
    n_warehouses = len(names)
    n_regions = len(demands)
    # the rules name the cities by their position in the list, as the reference does
    new_york, los_angeles, chicago, atlanta = range(4)

    # Every region receives exactly its demand. The problem asks for at least the
    # demand, but with non-negative unit costs an extra unit never lowers the cost,
    # so the optimum is unchanged; this bounds every shipment by its region's demand.
    if min(fixed_costs) < 0 or min(min(row) for row in costs) < 0:
        raise ValueError("costs are expected to be non-negative")

    m = Model()
    # open_warehouse[i] is true when warehouse i is open
    open_warehouse = m.bool_vector("open_warehouse", n_warehouses)
    # ships[i][j] = units sent from warehouse i to region j; at most max_shipping and
    # at most the region's demand (a range of one value is not an integer variable in
    # hermax, so a region without demand gets a spare value that is ruled out)
    ships = []
    for i in range(n_warehouses):
        row = []
        for j in range(n_regions):
            most = min(max_shipping, demands[j])
            x = m.int(f"ships_{i}_{j}", 0, max(most, 1))
            if most < 1:
                m &= ~(x >= 1)
            row.append(x)
        ships.append(row)
    # sent[i][j][k - 1] = "at least k units go from warehouse i to region j"
    sent = [[[ships[i][j] >= k for k in range(1, min(max_shipping, demands[j]) + 1)]
             for j in range(n_regions)] for i in range(n_warehouses)]

    # a closed warehouse ships nothing
    for i in range(n_warehouses):
        for j in range(n_regions):
            if sent[i][j]:
                m &= (open_warehouse[i] | ~sent[i][j][0])

    # each warehouse sends at most max_shipping units per week (a totalizer over its
    # shipments, cut just above the limit); full[i] says it sends exactly that many
    full = []
    for i in range(n_warehouses):
        out = unary_total(m, sent[i], max_shipping + 1)
        if len(out) > max_shipping:
            m &= ~out[max_shipping]
        full.append(out[max_shipping - 1] if max_shipping >= 1 and len(out) >= max_shipping else False)

    # every region receives its demand (exactly, see above)
    for j in range(n_regions):
        got = unary_total(m, [sent[i][j] for i in range(n_warehouses)], demands[j] + 1)
        if demands[j] > 0:
            m &= got[demands[j] - 1]
        if len(got) > demands[j]:
            m &= ~got[demands[j]]

    # 1. if the New York warehouse is open, the Los Angeles one must be open too
    m &= (~open_warehouse[new_york] | open_warehouse[los_angeles])
    # 2. at most three warehouses are open
    m &= (sum(1 * open_warehouse[i] for i in range(n_warehouses)) <= 3)
    # 3. the Atlanta or the Los Angeles warehouse (or both) must be open
    m &= (open_warehouse[atlanta] | open_warehouse[los_angeles])

    # Implied: the open warehouses must be able to send the total demand, so at
    # least ceil(total demand / max_shipping) of them are open.
    total_demand = sum(demands)
    if total_demand > 0:
        m &= (sum(1 * open_warehouse[i] for i in range(n_warehouses))
              >= -(-total_demand // max_shipping))

    # Dominance: a solution that one of the moves below makes strictly cheaper is not
    # optimal, so it is ruled out. Each move keeps every region's delivery, every
    # warehouse's total and the set of open warehouses, so it stays feasible, and no
    # optimal solution is removed.
    used = lambda i, j: sent[i][j][0] if sent[i][j] else False
    # (a) A unit sent from i to region j would be cheaper from an open warehouse i2
    #     that is not full.
    for j in range(n_regions):
        for i in range(n_warehouses):
            for i2 in range(n_warehouses):
                if costs[i2][j] < costs[i][j] and used(i, j) is not False and sent[i2][j]:
                    clause = ~used(i, j) | ~open_warehouse[i2]
                    if full[i2] is not False:
                        clause = clause | full[i2]
                    m &= clause
    # (b) Warehouses i_1..i_k sending to regions j_1..j_k: each i_t sending one unit to
    #     j_(t+1) instead of j_t (cyclically) changes the cost by
    #     sum c[i_t][j_(t+1)] - c[i_t][j_t]; when that is negative, the k shipments
    #     cannot all be positive.
    for k in CYCLE_LENGTHS:
        for whs in itertools.permutations(range(n_warehouses), k):
            if whs[0] != min(whs):  # each cycle once, starting at its lowest warehouse
                continue
            for regs in itertools.permutations(range(n_regions), k):
                change = sum(costs[whs[t]][regs[(t + 1) % k]] - costs[whs[t]][regs[t]]
                             for t in range(k))
                lits = [used(whs[t], regs[t]) for t in range(k)]
                if change < 0 and all(lit is not False for lit in lits):
                    m &= functools.reduce(operator.or_, [~lit for lit in lits])

    # Minimise the total cost. A soft clause pays its weight when its literal is
    # false, so a cost that is incurred when a literal is true is written negated.
    # Fixed costs: each open warehouse pays its fixed cost.
    for i in range(n_warehouses):
        if fixed_costs[i] > 0:
            m.obj[fixed_costs[i]] += ~open_warehouse[i]
    # Shipping costs, region by region. With the distinct unit costs into region j
    # sorted as v_1 < v_2 < ..., every one of its d_j units pays v_1, a constant that
    # is left out of the soft clauses, and a unit pays v_l - v_(l-1) more for every
    # level l >= 2 with v_l at most its own unit cost. Level l counts, in unary, the
    # units arriving from warehouses whose unit cost is at least v_l; the levels are
    # built from the dearest down, each adding the warehouses of the next lower cost,
    # and "at least k units counted at level l" pays v_l - v_(l-1).
    for j in range(n_regions):
        values = sorted({costs[i][j] for i in range(n_warehouses)})
        counted = []
        for level in range(len(values) - 1, 0, -1):
            here = [sent[i][j] for i in range(n_warehouses) if costs[i][j] == values[level]]
            counted = unary_total(m, [counted] + here, demands[j])
            step = values[level] - values[level - 1]
            for at_least_k in counted:
                m.obj[step] += ~at_least_k

    # total_cost is a declared output. It is added up as a binary number with adder
    # circuits (an equality between an integer and the cost sum is the encoding that
    # ran out of memory before) and the bits are then tied to an integer variable.
    # Each shipment enters through its binary digits, read off its unary literals.
    terms = [(fixed_costs[i], open_warehouse[i]) for i in range(n_warehouses) if fixed_costs[i] > 0]
    for i in range(n_warehouses):
        for j in range(n_regions):
            if costs[i][j] > 0 and sent[i][j]:
                for b, bit in enumerate(unary_to_bits(m, sent[i][j])):
                    terms.append((costs[i][j] << b, bit))
    bits = sum_bits(m, terms)
    # The total lies between every region paying its cheapest unit cost for all its
    # demand, and every region paying its dearest unit cost plus every fixed cost.
    lb = sum(demands[j] * min(costs[i][j] for i in range(n_warehouses)) for j in range(n_regions))
    ub = sum(fixed_costs) + sum(demands[j] * max(costs[i][j] for i in range(n_warehouses))
                                for j in range(n_regions))
    total_cost = integer_from_bits(m, bits, lb, ub, "total_cost")

    return m, {"total_cost": total_cost, "open_warehouse": open_warehouse, "ships": ships}
