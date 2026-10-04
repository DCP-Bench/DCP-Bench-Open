# Cabling: place 1U devices in distinct rack slots so that the total length
# of the cables between them (cable count times slot distance, per pair) is
# as short as possible.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]
    devices = instance["devices"]
    index = {name: i for i, name in enumerate(devices)}
    cables = [(index[a], index[b], num) for a, b, num in instance["cable_struct"]]
    slots = range(n)

    pool = IDPool()
    # x[d] is the rack slot of device d, 0..n-1. Direct encoding: the
    # distance rules below are stated per pair of slots.
    x = [Integer(f"x_{d}", 0, n - 1, vpool=pool) for d in range(n)]
    # dist[c] is the slot distance spanned by cable group c, 0..n-1. Order
    # encoding, so the length paid is a run of threshold literals.
    dist = [Integer(f"dist_{c}", 0, n - 1, encoding="order", vpool=pool)
            for c in range(len(cables))]
    # The sum of all cable lengths; at most (n - 1) times the total cable
    # count, since no two slots are further apart than n - 1.
    total_cables = sum(num for _, _, num in cables)
    final_sum = Integer("final_sum", 0, (n - 1) * total_cables,
                        encoding="order", vpool=pool)
    engine = IntegerEngine(vars=x + dist + [final_sum], vpool=pool)

    # All devices have distinct positions in the rack.
    engine.add_alldifferent(x)

    # The total length is the sum over cable groups of count times distance.
    engine.add_linear(sum(num * dist[c] for c, (_, _, num) in enumerate(cables))
                      - final_sum == 0)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Each cable group spans |x[a] - x[b]| slots: for every pair of slots the
    # two devices could occupy, the distance is pinned to that gap.
    for c, (a, b, _) in enumerate(cables):
        for k in slots:
            for m in slots:
                if k == m:
                    continue
                gap = abs(k - m)
                at = [-x[a].equals(k), -x[b].equals(m)]
                formula.append(at + [dist[c].ge(gap)])
                if gap + 1 <= n - 1:
                    formula.append(at + [-dist[c].ge(gap + 1)])

    # Symmetry breaking (own derivation): reversing the rack keeps every
    # distance and hence final_sum, the only declared output, so device 0 may
    # be required to sit above device 1.
    if n >= 2:
        for k in slots:
            for m in slots:
                if k >= m:
                    formula.append([-x[0].equals(k), -x[1].equals(m)])

    # Minimise the total cable length: cable group c pays its count for every
    # slot of distance it spans.
    for c, (_, _, num) in enumerate(cables):
        if num > 0:
            for v in range(1, n):
                formula.append([-dist[c].ge(v)], weight=num)

    return formula, {"final_sum": final_sum}
