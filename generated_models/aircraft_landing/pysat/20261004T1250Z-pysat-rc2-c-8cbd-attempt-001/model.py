# Aircraft landing with a fixed landing order: give every aircraft a landing
# time inside its window, keep the required separation between any two
# aircraft (aircraft i lands before aircraft j when i < j), and minimise the
# total penalty for landing before or after the target times.
from math import gcd

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer


def build(instance):
    earliest = instance["earliest_landing"]
    latest = instance["latest_landing"]
    target = instance["target_landing"]
    penalty_after = instance["penalty_after"]
    penalty_before = instance["penalty_before"]
    separation = instance["separation_time"]
    n = len(earliest)

    pool = IDPool()
    formula = WCNF()

    def ge(x, v):
        # The literal for "x >= v", or a constant outside x's domain.
        if v <= x.lb:
            return True
        if v > x.ub:
            return False
        return x.ge(v)

    def neg(lit):
        return (not lit) if isinstance(lit, bool) else -lit

    def clause(*lits):
        # Add a hard clause, dropping false constants; a true constant
        # satisfies it.
        if any(lit is True for lit in lits):
            return
        kept = [lit for lit in lits if lit is not False]
        if not kept:
            # Nothing left to satisfy: the instance is infeasible.
            dead = pool.id("infeasible")
            formula.append([dead])
            formula.append([-dead])
            return
        formula.append(kept)

    # landing_times[i] lies in aircraft i's window [earliest, latest]. The
    # coupled encoding gives both the "lands at time t" literals the runner
    # reads and the "lands at or after t" literals the separation and penalty
    # clauses are written with.
    landing_times = [Integer(f"landing_times_{i}", earliest[i], latest[i],
                             encoding="coupled", vpool=pool) for i in range(n)]
    for x in landing_times:
        formula.extend(x.domain_clauses())

    # Separation: aircraft j lands at least separation[i][j] after aircraft i
    # for every i < j. On the order literals this is one binary clause per
    # time t: if i lands at or after t then j lands at or after t + sep. That
    # is far smaller than a pseudo-Boolean encoding of the difference.
    for i in range(n):
        for j in range(i + 1, n):
            sep = separation[i][j]
            for t in range(earliest[i], latest[i] + 1):
                clause(neg(ge(landing_times[i], t)), ge(landing_times[j], t + sep))

    # Objective: each time unit an aircraft lands before its target pays
    # penalty_before, each unit after it pays penalty_after. "Lands before t"
    # for a t up to the target is the soft clause [x >= t]; "lands at or after
    # t" for a t beyond the target is the soft clause [x < t]. Units that every
    # time in the window pays (a target outside the window) are a constant and
    # are left out.
    for i in range(n):
        x = landing_times[i]
        for t in range(earliest[i] + 1, min(target[i], latest[i]) + 1):
            if penalty_before[i] > 0:
                formula.append([x.ge(t)], weight=penalty_before[i])
        for t in range(max(target[i], earliest[i]) + 1, latest[i] + 1):
            if penalty_after[i] > 0:
                formula.append([-x.ge(t)], weight=penalty_after[i])

    # total_penalty is a declared output, so it has to be an Integer equal to
    # the penalty sum. Its range comes from an upper bound on the optimum: the
    # penalty of landing every aircraft, in order, at the earliest time that
    # is no earlier than its window start and target and keeps the separation
    # from every earlier aircraft. When that schedule overruns a window, the
    # bound falls back to the worst penalty of each aircraft added up. No
    # optimal schedule costs more, so capping the total there loses none.
    def penalty_of(i, t):
        return (penalty_before[i] * max(0, target[i] - t)
                + penalty_after[i] * max(0, t - target[i]))

    times = []
    for j in range(n):
        t = max([earliest[j], target[j]]
                + [times[i] + separation[i][j] for i in range(j)])
        times.append(t)
    if all(times[i] <= latest[i] for i in range(n)):
        upper = sum(penalty_of(i, times[i]) for i in range(n))
    else:
        upper = sum(max(penalty_of(i, earliest[i]), penalty_of(i, latest[i]))
                    for i in range(n))

    # Every penalty is a multiple of the common divisor of the penalty rates,
    # so the sum is built in those units: the unary sums below grow with the
    # square of their range, and counting in units of 10 instead of 1 makes
    # them 100 times smaller.
    unit = 0
    for rate in list(penalty_before) + list(penalty_after):
        unit = gcd(unit, rate)
    unit = unit or 1
    cap = upper // unit

    # cost[i] is aircraft i's penalty in units, order encoded: cost[i] >= k
    # exactly when the aircraft lands at least ceil(k*unit/penalty_before)
    # before its target or ceil(k*unit/penalty_after) after it. A penalty
    # above the cap is ruled out.
    cost = []
    for i in range(n):
        x = landing_times[i]
        worst = max(penalty_of(i, earliest[i]), penalty_of(i, latest[i])) // unit
        c = Integer(f"cost_{i}", 0, min(worst, cap), encoding="order", vpool=pool)
        formula.extend(c.domain_clauses())
        for k in range(1, min(worst, cap + 1) + 1):
            early = False
            if penalty_before[i] > 0:
                d = -(-k * unit // penalty_before[i])
                early = neg(ge(x, target[i] - d + 1))
            late = False
            if penalty_after[i] > 0:
                d = -(-k * unit // penalty_after[i])
                late = ge(x, target[i] + d)
            reach = ge(c, k)
            clause(neg(early), reach)
            clause(neg(late), reach)
            clause(neg(reach), early, late)
        cost.append(c)

    # Running total: partial[j] = partial[j-1] + cost[j], each order encoded
    # over 0..cap, with clauses for both "at least" and "at most" so the sum
    # is exact (a sum above the cap is infeasible).
    def add_sum(s, a, b):
        for va in range(0, a.ub + 1):
            for vb in range(0, b.ub + 1):
                if va + vb >= 1:
                    clause(neg(ge(a, va)), neg(ge(b, vb)), ge(s, va + vb))
                clause(ge(a, va + 1), ge(b, vb + 1), neg(ge(s, va + vb + 1)))

    partial = cost[0]
    for j in range(1, n):
        top = min(cap, partial.ub + cost[j].ub)
        s = Integer(f"partial_{j}", 0, top, encoding="order", vpool=pool)
        formula.extend(s.domain_clauses())
        add_sum(s, partial, cost[j])
        partial = s

    # total_penalty = unit * (the running total over all aircraft).
    total_penalty = Integer("total_penalty", 0, unit * partial.ub,
                            encoding="coupled", vpool=pool)
    formula.extend(total_penalty.domain_clauses())
    for v in range(1, unit * partial.ub + 1):
        units = -(-v // unit)
        clause(neg(total_penalty.ge(v)), ge(partial, units))
        clause(neg(ge(partial, units)), total_penalty.ge(v))

    return formula, {"landing_times": landing_times, "total_penalty": total_penalty}
