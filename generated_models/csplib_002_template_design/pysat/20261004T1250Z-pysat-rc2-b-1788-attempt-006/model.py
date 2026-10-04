# Template design (CSPLib 2): fill the slots of each printing template with
# copies of the design variations and choose how many sheets to print from
# each template, so that every variation's demand is met with as few printed
# sheets as possible.
from math import isqrt

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc
from pysat.pb import EncType as PBType


def build(instance):
    n_slots = instance["n_slots"]
    n_templates = instance["n_templates"]
    n_var = instance["n_var"]
    demand = instance["demand"]
    templates = range(n_templates)
    variations = range(n_var)
    # Copies of a variation on a template lie in 0..n_var and sheets per
    # template in 1..max(demand), the domains the reference declares.

    # Bounds on the fewest sheets. Lower: every sheet carries n_slots copies,
    # so at least sum(demand) / n_slots sheets are printed (the reference's
    # implied constraint). Upper: a feasible plan. One template whose slots
    # go one per variation and then, one at a time, to the variation needing
    # the most sheets per copy, printed until every demand is met, with every
    # other template printed once; failing that, the reference's domain.
    lower = max(-(-sum(demand) // n_slots), n_templates)
    upper = n_templates * max(demand)
    # (The other templates need some layout: possible when n_slots <= n_var * n_var.)
    if n_var <= n_slots <= n_var * n_var and n_templates >= 1:
        copies = [1] * n_var
        for _ in range(n_slots - n_var):
            v = max(variations, key=lambda v: (-(-demand[v] // copies[v])
                                               if copies[v] < n_var else -1))
            copies[v] += 1
        if sum(copies) == n_slots and max(copies) <= n_var:
            sheets = max([1] + [-(-demand[v] // copies[v]) for v in variations])
            if sheets <= max(demand):
                upper = min(upper, sheets + n_templates - 1)
    lower = min(lower, upper)
    # No template prints more than what the other templates leave of the
    # upper bound, each of them printing at least once.
    p_max = max(min(max(demand), upper - (n_templates - 1)), 1)
    ub = max(p_max, 2)   # widened to 2 values at least, see below

    pool = IDPool()
    # production[t] is the number of sheets printed from template t.
    production = [Integer(f"production{t}", 1, ub, vpool=pool) for t in templates]
    # layout[t][v] is the number of copies of variation v on template t.
    layout = [[Integer(f"layout_{t}_{v}", 0, max(n_var, 1), vpool=pool) for v in variations]
              for t in templates]
    engine = IntegerEngine(vars=production + [x for row in layout for x in row], vpool=pool)

    # All slots are populated in a template.
    for t in templates:
        engine.add_linear(sum(layout[t]) == n_slots)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)
    # The domains are widened by one value where they would hold a single
    # value; that value is ruled out here.
    for t in templates:
        for v in range(p_max + 1, ub + 1):
            formula.append([-production[t].equals(v)])
        if n_var < 1:
            for v in variations:
                formula.append([-layout[t][v].equals(1)])

    # The products production[t] * layout[t][v] are not linear, so both
    # factors are spelled out in binary digits, value by value, and each
    # product is a weighted sum of digit pairs: the digit pair (b, c) is
    # worth 2^(b + c) sheets' worth of copies. pair[t][v][b][c] is true
    # exactly when both digits are 1, so the sum below sees the exact product.
    def digits(x, lo, hi, name):
        n = max(hi, 1).bit_length()
        bits = [pool.id((name, k)) for k in range(n)]
        for val in range(lo, hi + 1):
            for k in range(n):
                formula.append([-x.equals(val), bits[k] if (val >> k) & 1 else -bits[k]])
        return bits

    prod_bits = [digits(production[t], 1, ub, ("production bit", t)) for t in templates]
    layout_bits = [[digits(layout[t][v], 0, max(n_var, 1), ("layout bit", t, v))
                    for v in variations] for t in templates]

    # Meet demand: the copies of variation v printed over all templates,
    # sum over t of production[t] * layout[t][v], reach its demand. BDD
    # encoding: it propagates every consequence of the sum, which the more
    # compact adder does not; with the bound at most max(demand) the
    # diagram stays small.
    coverage = []
    for v in variations:
        lits, weights = [], []
        for t in templates:
            for b, pb in enumerate(prod_bits[t]):
                for c, lb in enumerate(layout_bits[t][v]):
                    pair = pool.id(("pair", t, v, b, c))
                    formula.append([-pair, pb])
                    formula.append([-pair, lb])
                    formula.append([pair, -pb, -lb])
                    lits.append(pair)
                    weights.append(1 << (b + c))
        formula.extend(PBEnc.geq(lits=lits, weights=weights, bound=demand[v], vpool=pool,
                                 encoding=PBType.bdd).clauses)
        coverage.append((lits, weights))

    # Implied (stated in the reference): every template fills all its slots,
    # so the sheets cover the total demand.
    formula.extend(PBEnc.geq(lits=[pb for t in templates for pb in prod_bits[t]],
                             weights=[n_slots << b for t in templates
                                      for b in range(len(prod_bits[t]))],
                             bound=sum(demand), vpool=pool, encoding=PBType.adder).clauses)

    # total is the number of sheets printed, within the bounds above. It is
    # stated as at least the sum of the templates' sheets; being minimised,
    # it equals that sum at the optimum. Adder encoding over the digits.
    total = Integer("total", lower, max(upper, lower + 1), encoding="order", vpool=pool)
    formula.extend(IntegerEngine(vars=[total], vpool=pool).clausify().clauses)
    if upper == lower:
        formula.append([-total.ge(upper + 1)])   # the widened value
    thresholds = [total.ge(v) for v in range(lower + 1, max(upper, lower + 1) + 1)]
    formula.extend(PBEnc.leq(lits=[pb for t in templates for pb in prod_bits[t]] + thresholds,
                             weights=[1 << b for t in templates
                                      for b in range(len(prod_bits[t]))]
                             + [-1] * len(thresholds),
                             bound=lower, vpool=pool, encoding=PBType.adder).clauses)

    # Implied upper bound on each variation's copies. The copies of all
    # variations add up to n_slots per sheet, so at most n_slots * total, and
    # every other variation takes at least its demand; what is left bounds
    # the copies of v. This tells the solver how little slack a small total
    # leaves. (copies of v) - n_slots * (total - lower) <= n_slots * lower -
    # (demand of the others), stated only when that bound is not negative,
    # as PBEnc refuses a negative bound. Adder encoding.
    for v in variations:
        lits, weights = coverage[v]
        rest = n_slots * lower - (sum(demand) - demand[v])
        if rest >= 0:
            formula.extend(PBEnc.leq(lits=lits + thresholds,
                                     weights=weights + [-n_slots] * len(thresholds),
                                     bound=rest, vpool=pool, encoding=PBType.adder).clauses)

    # Minimise the number of printed sheets: reaching total >= v pays a
    # weight that grows with v, so what is paid strictly rises with the
    # sheets printed. The weights come in about sqrt(N) groups, so stratified
    # RC2 settles a group at a time instead of one sheet per core.
    group = isqrt(max(upper - lower, 1)) + 1
    for v in range(lower + 1, upper + 1):
        formula.append([-total.ge(v)], weight=1 + (v - lower - 1) // group)

    return formula, {"production": production, "layout": layout}
