# Coins: choose how many coins of each denomination to carry so that every
# amount from 1 up to (but excluding) the maximum amount can be paid exactly
# from them, using as few coins as possible.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    denominations = instance["denominations"]
    max_amount = instance["max_amount_to_pay"]
    n = len(denominations)

    pool = IDPool()
    # x[i] is the number of coins of denomination i. The reference bounds it
    # by 0..max_amount. No payment below max_amount can use more than
    # (max_amount - 1) // d coins of value d, so carrying more is never part
    # of a fewest-coins answer; that tighter bound is used. Coupled encoding:
    # thresholds for the counting below, and value literals for the runner
    # to block a reported answer.
    ub = [max_amount if d <= 0 else min(max_amount, (max_amount - 1) // d)
          for d in denominations]
    x = [Integer(f"x_{i}", 0, ub[i], encoding="coupled", vpool=pool)
         for i in range(n)]
    engine = IntegerEngine(vars=list(x), vpool=pool)

    # Every amount j in 1..max_amount-1 can be paid exactly: tmp[i] coins of
    # denomination i, never more than are carried. A payment of j uses at
    # most j // d coins of value d, which bounds tmp[i]; order encoding,
    # since tmp only appears in weighted sums and comparisons.
    impossible = False
    pay = []
    for j in range(1, max_amount):
        terms = []
        for i, d in enumerate(denominations):
            top = ub[i] if d <= 0 else min(ub[i], j // d)
            if top <= 0:
                continue
            tmp = Integer(f"tmp_{j}_{i}", 0, top, encoding="order", vpool=pool)
            engine.add_var(tmp)
            terms.append((i, d, tmp, top))
        if not terms:
            impossible = True
            continue
        engine.add_linear(sum(d * tmp for _, d, tmp, _ in terms) == j)
        pay.extend((i, tmp, top) for i, _, tmp, top in terms)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)
    if impossible:
        # Some amount has no denomination small enough to pay it.
        formula.append([])

    # The coins used for a payment are among those carried: tmp[i] <= x[i].
    for i, tmp, top in pay:
        for v in range(1, top + 1):
            formula.append([-tmp.ge(v), x[i].ge(v)])

    # The total number of coins is at most max_amount, the reference's bound
    # on num_coins.
    if sum(ub) > max_amount:
        steps = [x[i].ge(v) for i in range(n) for v in range(1, ub[i] + 1)]
        formula.extend(CardEnc.atmost(lits=steps, bound=max_amount, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # Minimise the number of coins: each coin carried of each denomination
    # pays 1.
    for i in range(n):
        for v in range(1, ub[i] + 1):
            formula.append([-x[i].ge(v)], weight=1)

    return formula, {"x": x}
