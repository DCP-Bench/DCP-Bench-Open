# Airline revenue management: decide how many units of each itinerary package
# to sell, within each package's demand and each flight leg's seats, so that
# the total revenue is as large as possible.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc
from pysat.pb import EncType as PBType


def build(instance):
    available_seats = instance["available_seats"]
    demand = instance["demand"]
    revenue = instance["revenue"]
    delta = instance["delta"]          # delta[i][j] = 1 if package i uses leg j
    num_packages = len(demand)
    num_legs = len(available_seats)
    packages = range(num_packages)

    # The most units of package i that can ever be sold: its demand, and the
    # seats on every leg it uses.
    cap = []
    for i in packages:
        c = demand[i]
        for j in range(num_legs):
            if delta[i][j] > 0:
                c = min(c, available_seats[j] // delta[i][j])
        cap.append(max(c, 0))

    # Bounds on the best revenue. Selling packages greedily, highest revenue
    # first, each as far as seats and demand allow, is a feasible plan, so the
    # optimum earns at least that much; and it earns at most every package
    # sold up to its cap. max_revenue's domain is narrowed to this range,
    # which still contains every optimal value.
    seats = list(available_seats)
    lower = 0
    for i in sorted(packages, key=lambda i: -revenue[i]):
        if revenue[i] <= 0:
            break
        units = max(demand[i], 0)
        for j in range(num_legs):
            if delta[i][j] > 0:
                units = min(units, seats[j] // delta[i][j])
        units = max(units, 0)
        for j in range(num_legs):
            seats[j] -= delta[i][j] * units
        lower += revenue[i] * units
    upper = max(sum(max(revenue[i], 0) * cap[i] for i in packages), lower + 1)

    pool = IDPool()
    # packages_to_sell[i] is the number of units of package i sold, in
    # 0..max(demand) as in the reference. Coupled encoding: the order half
    # gives the seat sums and the per-unit revenue thresholds, the direct half
    # the "== v" literals the runner blocks on.
    top = max(max(demand), 1)
    packages_to_sell = [Integer(f"packages_to_sell{i}", 0, top, encoding="coupled",
                                vpool=pool) for i in packages]
    # max_revenue is the total revenue of the units sold.
    max_revenue = Integer("max_revenue", lower, upper, vpool=pool)
    engine = IntegerEngine(vars=packages_to_sell + [max_revenue], vpool=pool)

    # The units sold on each flight leg fit in its available seats.
    for j in range(num_legs):
        terms = [delta[i][j] * packages_to_sell[i] for i in packages if delta[i][j] != 0]
        if terms:
            engine.add_linear(sum(terms) <= available_seats[j])

    # No package sells more units than its demand.
    for i in packages:
        engine.add_linear(packages_to_sell[i] <= demand[i])

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # max_revenue is the revenue of the units sold. Its value is spelled out
    # in binary digits, offset from the lower bound, value by value; the
    # revenue is then one pseudo-Boolean equation over those digits and the
    # unit thresholds of the packages (adder encoding). A sum over
    # max_revenue's own value literals would carry thousands of distinct
    # weights.
    n_bits = (upper - lower).bit_length()
    bits = [pool.id(("revenue bit", k)) for k in range(n_bits)]
    for v in range(lower, upper + 1):
        for k in range(n_bits):
            formula.append([-max_revenue.equals(v),
                            bits[k] if ((v - lower) >> k) & 1 else -bits[k]])
    lits, weights = [], []
    for i in packages:
        if revenue[i] != 0:
            for v in range(1, top + 1):
                lits.append(packages_to_sell[i].ge(v))
                weights.append(revenue[i])
    lits += bits
    weights += [-(1 << k) for k in range(n_bits)]
    # revenue of the units sold - digits == lower; PBEnc refuses a negative
    # bound, and lower is never negative.
    formula.extend(PBEnc.equals(lits=lits, weights=weights, bound=lower, vpool=pool,
                                encoding=PBType.adder).clauses)

    # Maximise the revenue: every unit of package i left unsold, up to its
    # cap, pays its revenue, so RC2 minimises the shortfall from selling
    # every package up to its cap. (A package with a negative revenue pays
    # for each unit sold instead.)
    for i in packages:
        for v in range(1, top + 1):
            if revenue[i] > 0 and v <= cap[i]:
                formula.append([packages_to_sell[i].ge(v)], weight=revenue[i])
            elif revenue[i] < 0:
                formula.append([-packages_to_sell[i].ge(v)], weight=-revenue[i])

    return formula, {"packages_to_sell": packages_to_sell, "max_revenue": max_revenue}
