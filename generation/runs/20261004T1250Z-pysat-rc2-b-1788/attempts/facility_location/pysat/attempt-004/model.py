# Facility location: decide which of four candidate warehouses (New York, Los
# Angeles, Chicago, Atlanta) to open and how many units each ships to each
# region, meeting every region's demand at minimal fixed plus shipping cost,
# under three opening rules.
from itertools import product
from math import isqrt

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc
from pysat.pb import EncType as PBType


def build(instance):
    fixed_costs = instance["fixed_costs"]
    max_shipping = instance["max_shipping"]
    demands = instance["demands"]
    shipping_costs = instance["shipping_costs"]   # unit costs, non-negative in this problem
    num_companies = len(fixed_costs)
    num_regions = len(demands)
    companies = range(num_companies)
    regions = range(num_regions)
    # The warehouses are named by position, as in the reference.
    new_york, los_angeles, chicago, atlanta = range(4)
    # total_cost lies in 0..10000, the domain the reference declares.
    max_total = 10000
    demand = [max(d, 0) for d in demands]

    def allowed(opened):
        """The three opening rules."""
        return ((not opened[new_york] or opened[los_angeles])
                and sum(opened) <= 3
                and (opened[atlanta] or opened[los_angeles]))

    # Upper bound on the optimum: for every set of warehouses the rules allow,
    # ship each region's demand from its cheapest open warehouses with
    # capacity left. Each such plan is feasible, so the optimum costs at most
    # the cheapest of them (and at most 10000).
    upper = max_total
    for opened in product([False, True], repeat=num_companies):
        if not allowed(opened):
            continue
        left = [max_shipping if opened[i] else 0 for i in companies]
        cost = sum(fixed_costs[i] for i in companies if opened[i])
        need_left = 0
        for j in sorted(regions, key=lambda j: -demand[j]):
            need = demand[j]
            for i in sorted(companies, key=lambda i: shipping_costs[i][j]):
                take = min(need, left[i])
                left[i] -= take
                need -= take
                cost += take * shipping_costs[i][j]
            need_left += need
        if need_left == 0:
            upper = min(upper, cost)

    # Shipping beyond a region's demand never lowers the cost (unit costs are
    # non-negative), and cutting an excess back keeps a plan feasible, so some
    # optimal plan ships exactly the demand; that is the plan sought here.
    # Then, ranking the warehouses by unit cost to region j, the region's
    # shipping cost is
    #   cheapest unit cost * demand
    #   + sum over ranks k >= 2 of (cost of rank k - cost of rank k-1)
    #                              * (units j receives from ranks k and up).
    # Every term is non-negative; the levels this needs are linked to the
    # shipments by short clauses that unit propagation works through.
    rank = [sorted(companies, key=lambda i: shipping_costs[i][j]) for j in regions]
    base = sum(shipping_costs[rank[j][0]][j] * demand[j] for j in regions)
    lower = base + min(fixed_costs)      # at least one warehouse opens (rule 3)
    lower = max(0, min(lower, upper - 1))

    pool = IDPool()
    # open_warehouse[i] is true when warehouse i is opened.
    open_warehouse = [pool.id(("open", i)) for i in companies]
    # ships[i][j] is the number of units warehouse i ships to region j, in
    # 0..max_shipping as in the reference. Coupled encoding: the order half
    # gives the sums, the direct half the "== v" literals the runner blocks on.
    ships = [[Integer(f"ships_{i}_{j}", 0, max(max_shipping, 1), encoding="coupled",
                      vpool=pool) for j in regions] for i in companies]
    # total_cost, within the bounds derived above. Coupled encoding: the
    # objective pays on its thresholds, the digits below are read off its
    # value literals.
    total_cost = Integer("total_cost", lower, max(upper, lower + 1), encoding="coupled",
                         vpool=pool)
    engine = IntegerEngine(vars=[s for row in ships for s in row] + [total_cost], vpool=pool)
    engine.add_linear(total_cost <= upper)

    # Each warehouse ships at most max_shipping units per week in total...
    for i in companies:
        engine.add_linear(sum(ships[i]) <= max_shipping)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    def neg(lit):
        return (not lit) if isinstance(lit, bool) else -lit

    def clause(*lits):
        """Add a clause of literals, True (clause holds) or False (dropped)."""
        if any(lit is True for lit in lits):
            return
        formula.append([lit for lit in lits if lit is not False])

    # ...and ships nothing unless it is open.
    for i in companies:
        for j in regions:
            formula.append([open_warehouse[i], ships[i][j].equals(0)])

    # The shipments to each region meet its demand (exactly, see above).
    # level[j][k] counts the units region j receives from the warehouses
    # ranked k and up: level 0 is the whole demand, the level past the last
    # rank is 0, and each step removes one warehouse's shipment,
    #   level k = ships of the rank-k warehouse + level k + 1.
    # The levels in between are order-encoded in 0..demand[j], where such a
    # sum is a set of three-literal clauses in both directions.
    level = []
    for j in regions:
        d = demand[j]
        lits = {k: [pool.id(("level", j, k, v)) for v in range(1, d + 1)]
                for k in range(1, num_companies)}
        for k in lits:
            for v in range(1, d):
                formula.append([-lits[k][v], lits[k][v - 1]])

        def level_ge(k, v, d=d, lits=lits):
            if v <= 0:
                return True
            if v > d or k == num_companies:
                return False
            return True if k == 0 else lits[k][v - 1]

        def ship_ge(k, v, d=d, j=j):
            if v <= 0:
                return True
            if v > d or v > max(max_shipping, 1):
                return False
            return ships[rank[j][k]][j].ge(v)

        # no warehouse ships a region more than its demand
        for i in companies:
            if d + 1 <= max(max_shipping, 1):
                formula.append([-ships[i][j].ge(d + 1)])
        for k in range(num_companies):
            for a in range(0, d + 1):
                for b in range(0, d + 2 - a):
                    if a + b > 0:
                        # level k+1 >= a and the rank-k shipment >= b give level k >= a + b
                        clause(neg(level_ge(k + 1, a)), neg(ship_ge(k, b)), level_ge(k, a + b))
            for v in range(1, d + 1):
                for a in range(0, v):
                    # level k >= v needs level k+1 >= a + 1 or the rank-k shipment >= v - a
                    clause(neg(level_ge(k, v)), level_ge(k + 1, a + 1), ship_ge(k, v - a))
        level.append(level_ge)

    # 1. If the New York warehouse is opened, then the Los Angeles warehouse must be opened.
    formula.append([-open_warehouse[new_york], open_warehouse[los_angeles]])

    # 2. At most three warehouses can be opened.
    formula.extend(CardEnc.atmost(lits=open_warehouse, bound=3, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    # 3. Either the Atlanta or the Los Angeles warehouse must be opened.
    formula.append([open_warehouse[atlanta], open_warehouse[los_angeles]])

    # The cost terms beyond the constant `base`: fixed costs of the open
    # warehouses, and for each region and rank k >= 2 the step in unit cost
    # times each unit received from ranks k and up.
    terms = []
    for i in companies:
        if fixed_costs[i] > 0:
            terms.append((open_warehouse[i], fixed_costs[i]))
    for j in regions:
        for k in range(1, num_companies):
            step = shipping_costs[rank[j][k]][j] - shipping_costs[rank[j][k - 1]][j]
            if step > 0:
                for v in range(1, demand[j] + 1):
                    terms.append((level[j](k, v), step))

    # total_cost equals base plus those terms. Its value is spelled out in
    # binary digits, offset from its lower bound, value by value, and the
    # equation is stated over the digits and the terms (adder encoding):
    # sum of terms - digits == lower - base.
    top = max(upper, lower + 1)
    n_bits = max(top - lower, 1).bit_length()
    bits = [pool.id(("cost bit", b)) for b in range(n_bits)]
    for v in range(lower, top + 1):
        for b in range(n_bits):
            formula.append([-total_cost.equals(v), bits[b] if ((v - lower) >> b) & 1 else -bits[b]])
    lits = [lit for lit, _ in terms] + bits
    weights = [w for _, w in terms] + [-(1 << b) for b in range(n_bits)]
    rhs = lower - base
    if rhs < 0:      # PBEnc refuses a negative bound: negate the equation
        weights = [-w for w in weights]
        rhs = -rhs
    formula.extend(PBEnc.equals(lits=lits, weights=weights, bound=rhs, vpool=pool,
                                encoding=PBType.adder).clauses)

    # Minimise the total cost: reaching threshold v pays a weight that grows
    # with v, so what is paid strictly rises with total_cost and the cheapest
    # plan is the optimum. The weights come in about sqrt(N) groups, so
    # stratified RC2 settles a group at a time instead of raising its bound
    # one unit per core, and its cores stay single thresholds.
    group = isqrt(max(upper - lower, 1)) + 1
    for v in range(lower + 1, upper + 1):
        formula.append([-total_cost.ge(v)], weight=1 + (v - lower - 1) // group)

    return formula, {"total_cost": total_cost,
                     "open_warehouse": open_warehouse,
                     "ships": ships}
