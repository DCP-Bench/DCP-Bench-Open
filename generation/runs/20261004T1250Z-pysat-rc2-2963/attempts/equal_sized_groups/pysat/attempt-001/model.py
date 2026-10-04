# Equal sized groups: split a sorted list of n elements into k groups by
# choosing k - 1 break points, never separating equal values, so that the
# total deviation of the group sizes from round(n / k) is minimal.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    a = instance["a"]
    k = instance["k"]
    n = len(a)
    # The ideal group size, with Python's round as in the reference.
    gsize = round(n / k)
    breaks = range(k - 1)

    pool = IDPool()
    # x[p] is the 1-based index of the last element before break p. The
    # reference allows 1..n; a break at n would leave the last group empty,
    # so 1..n-1. Direct encoding: each group's size is read off a pair of
    # break values.
    x = [Integer(f"x_{p}", 1, n - 1, vpool=pool) for p in breaks]
    # err[i] is |size of group i - gsize|. A group holds 1..n-k+1 elements,
    # which bounds it. Order encoding: the objective pays one unit per
    # threshold reached.
    top = max(gsize - 1, n - k + 1 - gsize, 0)
    err = [Integer(f"err_{i}", 0, top, encoding="order", vpool=pool)
           for i in range(k)]
    engine = IntegerEngine(vars=x + err, vpool=pool)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Same values must be in the same group: no break between positions j
    # and j + 1 (1-based) when a[j-1] == a[j]. Only the remaining positions
    # are candidate break values below.
    allowed = [j for j in range(1, n) if a[j - 1] != a[j]]
    for p in breaks:
        for j in range(1, n):
            if a[j - 1] == a[j]:
                formula.append([-x[p].equals(j)])

    def charge(i, size, at):
        # Group i of this size forces err[i] up to its deviation.
        dev = abs(size - gsize)
        if dev > 0:
            formula.append(at + [err[i].ge(dev)])

    if k == 1:
        charge(0, n, [])
    else:
        # The first group's size is the first break point.
        for u in allowed:
            charge(0, u, [-x[0].equals(u)])
        # Each middle group's size is the gap between consecutive break
        # points, and every group holds at least one element, so the breaks
        # increase strictly.
        for i in range(1, k - 1):
            for u in allowed:
                for v in allowed:
                    at = [-x[i - 1].equals(u), -x[i].equals(v)]
                    if v <= u:
                        formula.append(at)
                    else:
                        charge(i, v - u, at)
        # The last group runs from the last break point to n.
        for u in allowed:
            charge(k - 1, n - u, [-x[k - 2].equals(u)])

    # The total error z is at most n (the domain of z in the reference).
    # The clauses above only force err[i] from below, so it is turned into
    # binary digits that are likewise forced at least as high as err[i]; a
    # sum of
    # k * log(top) weighted bits is far smaller than a cardinality
    # constraint over every threshold of every err[i].
    bits, weights = [], []
    for i in range(k):
        b = 0
        while (1 << b) <= top:
            bit = pool.id(("err_bit", i, b))
            # err[i] in an interval of values whose binary digit b is 1
            # forces the bit.
            lo = 1 << b
            while lo <= top:
                hi = min(lo + (1 << b) - 1, top)
                clause = [-err[i].ge(lo), bit]
                if hi < top:
                    clause.insert(1, err[i].ge(hi + 1))
                formula.append(clause)
                lo += 1 << (b + 1)
            bits.append(bit)
            weights.append(1 << b)
            b += 1
    if bits:
        formula.extend(PBEnc.leq(lits=bits, weights=weights, bound=n,
                                 vpool=pool).clauses)

    # Minimise the total error: every unit of deviation of every group pays 1.
    for i in range(k):
        for v in range(1, top + 1):
            formula.append([-err[i].ge(v)], weight=1)

    return formula, {"x": x}
