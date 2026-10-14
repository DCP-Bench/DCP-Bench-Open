# Multi-commodity transportation: ship each product from origins to
# destinations within every origin's supply and every lane's total limit,
# meeting every destination's demand, at the least total shipping cost.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    supply = instance["supply"]  # supply[i][p]
    demand = instance["demand"]  # demand[j][p]
    limit = instance["limit"]  # limit[i][j]
    cost = instance["cost"]  # cost[i][j][p], per unit shipped
    n_origins = len(supply)
    n_destinations = len(demand)
    n_products = len(supply[0])
    max_supply = max(max(row) for row in supply)

    pool = IDPool()

    # x[i][j][p] is the amount of product p shipped from origin i to
    # destination j. The reference allows 0..max_supply; no shipment can
    # exceed its origin's supply of p or its lane's limit either, so the
    # smallest of the three bounds it. Coupled encoding: the order literals
    # state the sums, the value literals build the cost below.
    x = [[[Integer(f"x_{i}_{j}_{p}", 0,
                   max(min(max_supply, supply[i][p], limit[i][j]), 1),
                   encoding="coupled", vpool=pool)
           for p in range(n_products)] for j in range(n_destinations)]
         for i in range(n_origins)]
    flat = [x[i][j][p] for i in range(n_origins) for j in range(n_destinations)
            for p in range(n_products)]
    engine = IntegerEngine(vars=flat, vpool=pool)

    # An origin ships no more of a product than it has.
    for i in range(n_origins):
        for p in range(n_products):
            engine.add_linear(sum(x[i][j][p] for j in range(n_destinations)) <= supply[i][p])

    # Each destination receives at least its demand of each product. With no
    # negative shipping cost, delivering more than the demand never lowers
    # the cost (any surplus can be left unshipped without breaking a supply
    # or lane limit), so the least cost is reached delivering exactly the
    # demand, and that is what is required. The only declared output is the
    # cost, which this does not change.
    exact = all(c >= 0 for plane in cost for row in plane for c in row)
    for j in range(n_destinations):
        for p in range(n_products):
            delivered = sum(x[i][j][p] for i in range(n_origins))
            if exact:
                engine.add_linear(delivered == demand[j][p])
            else:
                engine.add_linear(delivered >= demand[j][p])

    # The total shipped on a lane, over all products, stays within its limit.
    for i in range(n_origins):
        for j in range(n_destinations):
            engine.add_linear(sum(x[i][j][p] for p in range(n_products)) <= limit[i][j])

    formula = WCNF()
    formula.extend(engine.clausify().clauses)
    true = pool.id("true")
    formula.append([true])
    false = -true

    # total_cost, the declared output, is built in binary. Shipping v units
    # on a lane costs cost * v, and bit k of that is set exactly when the
    # shipment takes one of the values v whose cost has bit k set: an OR of
    # value literals. The per-shipment costs are added with ripple-carry
    # adders, a circuit small enough to leave the search to the soft clauses.
    def full_adder(a, b, c):
        s, carry = pool.id(), pool.id()
        for va in (True, False):
            for vb in (True, False):
                for vc in (True, False):
                    odd = va ^ vb ^ vc
                    formula.append([-a if va else a, -b if vb else b,
                                    -c if vc else c, s if odd else -s])
        formula.extend([[-a, -b, carry], [-a, -c, carry], [-b, -c, carry],
                        [a, b, -carry], [a, c, -carry], [b, c, -carry]])
        return s, carry

    def add(xs, ys):
        length = max(len(xs), len(ys))
        xs = xs + [false] * (length - len(xs))
        ys = ys + [false] * (length - len(ys))
        out, carry = [], false
        for a, b in zip(xs, ys):
            s, carry = full_adder(a, b, carry)
            out.append(s)
        return out + [carry]

    total = [false]
    upper = 0
    for i in range(n_origins):
        for j in range(n_destinations):
            for p in range(n_products):
                var, c = x[i][j][p], cost[i][j][p]
                most = c * var.ub
                upper += most
                term = []
                for k in range(max(most.bit_length(), 1)):
                    values = [var.equals(v) for v in range(var.lb, var.ub + 1)
                              if ((c * v) >> k) & 1]
                    if not values:
                        term.append(false)
                        continue
                    bit = pool.id()
                    formula.append([-bit] + values)
                    for lit in values:
                        formula.append([-lit, bit])
                    term.append(bit)
                total = add(total, term)

    # total_cost is an Integer over 0..(the cost of shipping every lane at
    # its upper bound), each value literal true exactly when the bits spell
    # that value. The bits spell exactly one value, so no exactly-one is
    # needed; bits beyond the width of the upper bound are zero.
    upper = max(upper, 1)
    width = upper.bit_length()
    for k in range(width, len(total)):
        formula.append([-total[k]])
    bits = (total + [false] * width)[:width]
    total_cost = Integer("total_cost", 0, upper, vpool=pool)
    for v in range(0, upper + 1):
        lit = total_cost.equals(v)
        spelled = [bits[k] if (v >> k) & 1 else -bits[k] for k in range(width)]
        for s in spelled:
            formula.append([-lit, s])
        formula.append([lit] + [-s for s in spelled])

    # Minimise the shipping cost: every unit of product p shipped from i to j
    # pays cost[i][j][p]. When deliveries equal the demand, every unit
    # delivered to j of product p costs at least the cheapest origin's price,
    # and those units add up to a constant; only the excess over the cheapest
    # price is paid in the soft clauses, which leaves the optimum where it is
    # and gives RC2 far fewer and lighter soft clauses to work through.
    for j in range(n_destinations):
        for p in range(n_products):
            cheapest = min(cost[i][j][p] for i in range(n_origins)) if exact else 0
            for i in range(n_origins):
                c = cost[i][j][p] - cheapest
                if c > 0:
                    for v in range(1, x[i][j][p].ub + 1):
                        formula.append([-x[i][j][p].ge(v)], weight=c)

    return formula, {"total_cost": total_cost}
