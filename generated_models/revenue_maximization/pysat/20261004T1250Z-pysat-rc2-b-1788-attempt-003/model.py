# Airline revenue management: decide how many units of each itinerary package
# to sell, within each package's demand and each flight leg's seats, so that
# the total revenue is as large as possible.
from math import isqrt

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    available_seats = instance["available_seats"]
    demand = instance["demand"]
    revenue = instance["revenue"]
    delta = instance["delta"]          # delta[i][j] = 1 if package i uses leg j
    num_packages = len(demand)
    num_legs = len(available_seats)
    packages = range(num_packages)

    # The most units of package i an optimal plan sells: its demand, and the
    # seats on every leg it uses. A package earning nothing per unit is never
    # needed, so an optimal plan exists that sells none of it.
    cap = []
    for i in packages:
        c = demand[i] if revenue[i] > 0 else 0
        for j in range(num_legs):
            if delta[i][j] > 0:
                c = min(c, available_seats[j] // delta[i][j])
        cap.append(max(c, 0))

    # Bounds on the best revenue. Selling packages greedily, highest revenue
    # first, each as far as seats and demand allow, is a feasible plan, so the
    # optimum earns at least that much (lower); it earns at most every package
    # sold up to its cap (upper). max_revenue's domain is this range, which
    # holds every optimal value.
    seats = list(available_seats)
    lower = 0
    for i in sorted(packages, key=lambda i: -revenue[i]):
        if cap[i] == 0:
            continue
        units = cap[i]
        for j in range(num_legs):
            if delta[i][j] > 0:
                units = min(units, seats[j] // delta[i][j])
        for j in range(num_legs):
            seats[j] -= delta[i][j] * units
        lower += revenue[i] * units
    upper = max(sum(revenue[i] * cap[i] for i in packages), lower + 1)

    pool = IDPool()
    # packages_to_sell[i] is the number of units of package i sold, in
    # 0..max(demand) as in the reference. Coupled encoding: the order half
    # gives the seat sums, the direct half the "== u" literals used below
    # and by the runner.
    top = max(max(demand), 1)
    packages_to_sell = [Integer(f"packages_to_sell{i}", 0, top, encoding="coupled",
                                vpool=pool) for i in packages]
    # max_revenue is the total revenue of the units sold. Coupled encoding:
    # the objective pays on its thresholds, the running sum below fixes its
    # value literals.
    max_revenue = Integer("max_revenue", lower, upper, encoding="coupled", vpool=pool)
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

    # Units beyond a package's cap are never part of an optimal plan (see above).
    for i in packages:
        for u in range(cap[i] + 1, top + 1):
            formula.append([-packages_to_sell[i].equals(u)])

    # max_revenue is the revenue of the units sold, tied to the sales by a
    # running sum over the packages: partial[s] is true when the packages
    # taken so far earn s. Partial sums above upper, or too small to reach
    # lower with everything that is left, are dropped, which is what keeps
    # this small; the running sum fixes max_revenue by unit propagation once
    # the sales are fixed, where a linear constraint over max_revenue's
    # thousands of values would not.
    order = sorted(packages, key=lambda i: -revenue[i] * cap[i])
    rest = [sum(revenue[i] * cap[i] for i in order[k:]) for k in range(num_packages + 1)]
    start = pool.id(("partial", 0, 0))
    formula.append([start])
    partial = {0: start}
    for k, i in enumerate(order):
        nxt = {}
        for s, lit in partial.items():
            for u in range(cap[i] + 1):
                w = s + revenue[i] * u
                if w > upper or w + rest[k + 1] < lower:
                    # selling u here cannot lead to an optimal plan
                    formula.append([-lit, -packages_to_sell[i].equals(u)])
                    continue
                if w not in nxt:
                    nxt[w] = pool.id(("partial", k + 1, w))
                formula.append([-lit, -packages_to_sell[i].equals(u), nxt[w]])
        partial = nxt
    for s, lit in partial.items():
        formula.append([-lit, max_revenue.equals(s)])
    for v in range(lower, upper + 1):
        if v not in partial:
            formula.append([-max_revenue.equals(v)])

    # Maximise the revenue: failing to reach threshold v pays a weight that
    # grows as v falls, so the total paid strictly falls as max_revenue
    # rises and the best revenue is the cheapest. The weights come in about
    # sqrt(N) groups rather than one per value, so stratified RC2 settles a
    # group at a time instead of raising its bound one unit per core.
    span = upper - lower
    group = isqrt(span) + 1
    for v in range(lower + 1, upper + 1):
        formula.append([max_revenue.ge(v)], weight=1 + (upper - v) // group)

    return formula, {"packages_to_sell": packages_to_sell, "max_revenue": max_revenue}
