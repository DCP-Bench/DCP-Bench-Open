# Warehouse location (CSPLib 34): decide which warehouses to open and which
# open warehouse supplies each store, within warehouse capacities, minimising
# maintenance plus supply costs.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    n_suppliers = instance["n_suppliers"]
    n_stores = instance["n_stores"]
    building_cost = instance["building_cost"]
    capacity = instance["capacity"]
    cost = instance["cost_matrix"]
    warehouses = range(n_suppliers)
    stores = range(n_stores)

    pool = IDPool()
    # supplier_assignment[s] is the warehouse supplying store s,
    # 0..n_suppliers-1. Direct encoding: costs and capacities are stated per
    # (store, warehouse) literal.
    supplier = [Integer(f"supplier_assignment_{s}", 0, n_suppliers - 1, vpool=pool)
                for s in stores]
    # open_warehouses[w] is true when warehouse w is open.
    is_open = [pool.id(("open", w)) for w in warehouses]
    # total_cost lies between every store at its cheapest warehouse with no
    # maintenance, and every store at its dearest with every warehouse open.
    # Coupled encoding: thresholds to sum it, and value literals for the
    # runner to block a reported answer.
    low = sum(min(cost[s]) for s in stores)
    high = sum(max(cost[s]) for s in stores) + building_cost * n_suppliers
    total_cost = Integer("total_cost", low, high, encoding="coupled", vpool=pool)
    engine = IntegerEngine(vars=supplier + [total_cost], vpool=pool)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    def serves(s, w):
        return supplier[s].equals(w)

    # The number of stores assigned to a warehouse cannot exceed its capacity.
    for w in warehouses:
        formula.extend(CardEnc.atmost(lits=[serves(s, w) for s in stores],
                                      bound=max(capacity[w], 0), vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # A warehouse is open if and only if it supplies at least one store.
    for w in warehouses:
        for s in stores:
            formula.append([-serves(s, w), is_open[w]])
        formula.append([-is_open[w]] + [serves(s, w) for s in stores])

    # total_cost is the supply cost of every store at its warehouse plus the
    # maintenance cost of every open warehouse: those terms minus the
    # thresholds of total_cost above its lower bound equal that lower bound.
    lits, weights = [], []
    for s in stores:
        for w in warehouses:
            lits.append(serves(s, w))
            weights.append(cost[s][w])
    for w in warehouses:
        lits.append(is_open[w])
        weights.append(building_cost)
    for v in range(low + 1, high + 1):
        lits.append(total_cost.ge(v))
        weights.append(-1)
    formula.extend(PBEnc.equals(lits=lits, weights=weights, bound=low,
                                vpool=pool).clauses)

    # Minimise the total cost: a store supplied by warehouse w pays its supply
    # cost, and an open warehouse pays the maintenance cost.
    for s in stores:
        for w in warehouses:
            if cost[s][w] > 0:
                formula.append([-serves(s, w)], weight=cost[s][w])
    if building_cost > 0:
        for w in warehouses:
            formula.append([-is_open[w]], weight=building_cost)

    return formula, {"total_cost": total_cost, "open_warehouses": is_open,
                     "supplier_assignment": supplier}
