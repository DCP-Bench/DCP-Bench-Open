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
    shipping_costs = instance["shipping_costs"]
    num_companies = len(fixed_costs)
    num_regions = len(demands)
    companies = range(num_companies)
    regions = range(num_regions)
    # The warehouses are named by position, as in the reference.
    new_york, los_angeles, chicago, atlanta = range(4)
    # total_cost lies in 0..10000, the domain the reference declares.
    max_total = 10000

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
        feasible = True
        for j in sorted(regions, key=lambda j: -demands[j]):
            need = max(demands[j], 0)
            for i in sorted(companies, key=lambda i: shipping_costs[i][j]):
                take = min(need, left[i])
                left[i] -= take
                need -= take
                cost += take * shipping_costs[i][j]
            feasible = feasible and need == 0
        if feasible:
            upper = min(upper, cost)
    # Lower bound: every unit of demand costs at least the cheapest unit
    # shipping cost to its region, and at least one warehouse is open (rule 3).
    lower = (sum(max(demands[j], 0) * min(shipping_costs[i][j] for i in companies)
                 for j in regions) + min(fixed_costs))
    lower = max(0, min(lower, upper - 1))

    pool = IDPool()
    # open_warehouse[i] is true when warehouse i is opened.
    open_warehouse = [pool.id(("open", i)) for i in companies]
    # ships[i][j] is the number of units warehouse i ships to region j, in
    # 0..max_shipping as in the reference. Coupled encoding: the order half
    # gives the sums and the per-unit cost thresholds, the direct half the
    # "== v" literals the runner blocks on.
    ships = [[Integer(f"ships_{i}_{j}", 0, max(max_shipping, 1), encoding="coupled",
                      vpool=pool) for j in regions] for i in companies]
    # total_cost, within the bounds derived above. Coupled: the objective pays
    # on its thresholds.
    total_cost = Integer("total_cost", lower, max(upper, lower + 1), encoding="coupled",
                         vpool=pool)
    engine = IntegerEngine(vars=[s for row in ships for s in row] + [total_cost], vpool=pool)
    engine.add_linear(total_cost <= upper)

    # Each warehouse ships at most max_shipping units per week in total...
    for i in companies:
        engine.add_linear(sum(ships[i]) <= max_shipping)

    # The shipments to each region meet its demand. With no negative cost,
    # shipping beyond the demand never lowers the cost, and cutting an excess
    # back keeps a plan feasible, so some optimal plan ships exactly the
    # demand; the equality is stated then, as it narrows the search.
    exact = all(c >= 0 for row in shipping_costs for c in row)
    for j in regions:
        received = sum(ships[i][j] for i in companies)
        if exact:
            engine.add_linear(received == demands[j])
        else:
            engine.add_linear(received >= demands[j])

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # ...and ships nothing unless it is open.
    for i in companies:
        for j in regions:
            formula.append([open_warehouse[i], ships[i][j].equals(0)])

    # 1. If the New York warehouse is opened, then the Los Angeles warehouse must be opened.
    formula.append([-open_warehouse[new_york], open_warehouse[los_angeles]])

    # 2. At most three warehouses can be opened.
    formula.extend(CardEnc.atmost(lits=open_warehouse, bound=3, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    # 3. Either the Atlanta or the Los Angeles warehouse must be opened.
    formula.append([open_warehouse[atlanta], open_warehouse[los_angeles]])

    # total_cost is at least the fixed cost of the open warehouses plus the
    # unit shipping cost of every unit shipped (each threshold ships >= v).
    # Only this direction is stated: total_cost is minimised, so at the
    # optimum it equals the cost of the plan reported with it. Adder
    # encoding, since thousands of literals take part.
    lits, weights = [], []
    for i in companies:
        if fixed_costs[i] != 0:
            lits.append(open_warehouse[i])
            weights.append(fixed_costs[i])
        for j in regions:
            if shipping_costs[i][j] != 0:
                for v in range(1, max_shipping + 1):
                    lits.append(ships[i][j].ge(v))
                    weights.append(shipping_costs[i][j])
    for v in range(lower + 1, max(upper, lower + 1) + 1):
        lits.append(total_cost.ge(v))
        weights.append(-1)
    # fixed + shipping - (total_cost - lower) <= lower; PBEnc refuses a
    # negative bound and lower is never negative.
    formula.extend(PBEnc.leq(lits=lits, weights=weights, bound=lower, vpool=pool,
                             encoding=PBType.adder).clauses)

    # Minimise the total cost: reaching threshold v pays a weight that grows
    # with v, so the total paid strictly rises with total_cost and the
    # cheapest plan is the optimum. The weights come in about sqrt(N) groups,
    # so stratified RC2 settles a group at a time instead of raising its
    # bound one unit per core.
    group = isqrt(max(upper - lower, 1)) + 1
    for v in range(lower + 1, upper + 1):
        formula.append([-total_cost.ge(v)], weight=1 + (v - lower - 1) // group)

    return formula, {"total_cost": total_cost,
                     "open_warehouse": open_warehouse,
                     "ships": ships}
