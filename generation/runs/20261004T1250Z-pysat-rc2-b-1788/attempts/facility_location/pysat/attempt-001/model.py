# Facility location: decide which of four candidate warehouses (New York, Los
# Angeles, Chicago, Atlanta) to open and how many units each ships to each
# region, meeting every region's demand at minimal fixed plus shipping cost,
# under three opening rules.
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
    # The warehouses are named by position, as in the reference.
    new_york, los_angeles, chicago, atlanta = range(4)
    # total_cost lies in 0..10000, the domain the reference declares.
    max_total = 10000

    pool = IDPool()
    # open_warehouse[i] is true when warehouse i is opened.
    open_warehouse = [pool.id(("open", i)) for i in range(num_companies)]
    # ships[i][j] is the number of units warehouse i ships to region j, in
    # 0..max_shipping as in the reference. Coupled encoding: the order half
    # gives the sums and the per-unit cost thresholds, the direct half the
    # "== v" literals the runner blocks on.
    ships = [[Integer(f"ships_{i}_{j}", 0, max(max_shipping, 1), encoding="coupled", vpool=pool)
              for j in range(num_regions)] for i in range(num_companies)]
    # total_cost is the fixed costs of the open warehouses plus the shipping costs.
    total_cost = Integer("total_cost", 0, max_total, encoding="coupled", vpool=pool)
    engine = IntegerEngine(vars=[s for row in ships for s in row] + [total_cost], vpool=pool)

    # Each warehouse ships at most max_shipping units per week in total...
    for i in range(num_companies):
        engine.add_linear(sum(ships[i]) <= max_shipping)

    # The shipments to each region meet its demand.
    for j in range(num_regions):
        engine.add_linear(sum(ships[i][j] for i in range(num_companies)) >= demands[j])

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # ...and ships nothing unless it is open.
    for i in range(num_companies):
        for j in range(num_regions):
            formula.append([open_warehouse[i], ships[i][j].equals(0)])

    # total_cost equals the fixed cost of every open warehouse plus, for every
    # unit shipped, its unit shipping cost. Each unit is one order threshold
    # ships >= v, weighted by the unit cost, and total_cost is its own order
    # thresholds at weight 1. The adder encoding is used because these are
    # over ten thousand literals; a BDD over them would be enormous.
    lits, weights = [], []
    for v in range(1, max_total + 1):
        lits.append(total_cost.ge(v))
        weights.append(1)
    for i in range(num_companies):
        if fixed_costs[i] != 0:
            lits.append(open_warehouse[i])
            weights.append(-fixed_costs[i])
        for j in range(num_regions):
            if shipping_costs[i][j] != 0:
                for v in range(1, max_shipping + 1):
                    lits.append(ships[i][j].ge(v))
                    weights.append(-shipping_costs[i][j])
    formula.extend(PBEnc.equals(lits=lits, weights=weights, bound=0, vpool=pool,
                                encoding=PBType.adder).clauses)

    # 1. If the New York warehouse is opened, then the Los Angeles warehouse must be opened.
    formula.append([-open_warehouse[new_york], open_warehouse[los_angeles]])

    # 2. At most three warehouses can be opened.
    formula.extend(CardEnc.atmost(lits=open_warehouse, bound=3, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    # 3. Either the Atlanta or the Los Angeles warehouse must be opened.
    formula.append([open_warehouse[atlanta], open_warehouse[los_angeles]])

    # Minimise the total cost. Opening warehouse i pays its fixed cost; every
    # unit shipped from i to j (each threshold ships >= v) pays the unit
    # shipping cost. A negative cost is paid when the literal is false, which
    # differs from the cost by a constant.
    def pay(lit, w):
        if w > 0:
            formula.append([-lit], weight=w)
        elif w < 0:
            formula.append([lit], weight=-w)

    for i in range(num_companies):
        pay(open_warehouse[i], fixed_costs[i])
        for j in range(num_regions):
            for v in range(1, max_shipping + 1):
                pay(ships[i][j].ge(v), shipping_costs[i][j])

    return formula, {"total_cost": total_cost,
                     "open_warehouse": open_warehouse,
                     "ships": ships}
