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
    # implied constraint), and every template prints at least one. Upper: a
    # feasible plan. One template whose slots go one per variation and then,
    # one at a time, to the variation needing the most sheets per copy,
    # printed until every demand is met, with every other template printed
    # once (any layout of them works when n_slots <= n_var * n_var); failing
    # that, the reference's domain.
    lower = max(-(-sum(demand) // n_slots), n_templates)
    upper = n_templates * max(demand)
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

    pool = IDPool()
    # production[t] is the number of sheets printed from template t. Coupled
    # encoding: the order half carries "at least so many sheets", the direct
    # half the "== v" literals the runner blocks on.
    production = [Integer(f"production{t}", 1, max(p_max, 2), encoding="coupled", vpool=pool)
                  for t in templates]
    # layout[t][v] is the number of copies of variation v on template t.
    layout = [[Integer(f"layout_{t}_{v}", 0, max(n_var, 1), vpool=pool) for v in variations]
              for t in templates]
    # total is the number of sheets printed, within the bounds above.
    total = Integer("total", lower, max(upper, lower + 1), encoding="order", vpool=pool)
    engine = IntegerEngine(vars=production + [x for row in layout for x in row] + [total],
                           vpool=pool)

    # All slots are populated in a template.
    for t in templates:
        engine.add_linear(sum(layout[t]) == n_slots)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    def clause(*lits):
        """Add a clause given literals, True (clause holds) or False (dropped)."""
        if any(lit is True for lit in lits):
            return
        formula.append([lit for lit in lits if lit is not False])

    # The domains are widened by one value where they would hold a single
    # value; that value is ruled out here.
    for t in templates:
        if p_max < 2:
            clause(-production[t].ge(2))
        if n_var < 1:
            for v in variations:
                clause(-layout[t][v].equals(1))
    if upper == lower:
        clause(-total.ge(upper + 1))

    def unary(name, cap):
        """Order literals x >= 1 .. x >= cap of a value in 0..cap."""
        lits = [pool.id((name, x)) for x in range(1, cap + 1)]
        for x in range(1, cap):
            formula.append([-lits[x], lits[x - 1]])
        return lits

    def ge(lits, x):
        """The literal for x-th threshold: True below 1, False past the top."""
        if x <= 0:
            return True
        if x > len(lits):
            return False
        return lits[x - 1]

    def p_ge(t, x):
        return True if x <= 1 else (False if x > p_max else production[t].ge(x))

    # Meet demand: the copies of variation v printed over all templates,
    # sum over t of production[t] * layout[t][v], reach its demand.
    # The product is not linear, so each template's share is a value
    # share[t][v] in 0..demand[v] (more is never needed), allowed to reach x
    # only when the template prints at least ceil(x / k) sheets with k copies
    # of v on it. Every share and partial sum is in order encoding, where
    # "a + b >= x" is a set of three-literal clauses, so the solver deduces
    # the sheets a template still owes as soon as the others are bounded.
    for v in variations:
        d = max(demand[v], 0)
        if d == 0:
            continue
        shares = []
        for t in templates:
            share = unary(("share", t, v), d)
            for x in range(1, d + 1):
                clause(-share[x - 1], -layout[t][v].equals(0))
                for k in range(1, max(n_var, 1) + 1):
                    clause(-share[x - 1], -layout[t][v].equals(k), p_ge(t, -(-x // k)))
            shares.append(share)
        # Running sum of the shares, capped at the demand: partial >= x only
        # when the shares so far add up to x.
        partial = shares[0]
        for t in range(1, n_templates - 1):
            merged = unary(("partial", t, v), d)
            for x in range(1, d + 1):
                for a in range(0, x):
                    # partial + shares[t] >= x needs shares[t] >= x - a when partial < a + 1
                    clause(-merged[x - 1], ge(partial, a + 1), ge(shares[t], x - a))
            partial = merged
        if n_templates == 1:
            clause(ge(partial, d))
        else:
            last = shares[-1]
            for a in range(0, d):
                clause(ge(partial, a + 1), ge(last, d - a))

    # total is at least the sheets of all templates; being minimised, it
    # equals their sum at the optimum. Adder encoding over the threshold
    # literals of the templates and of the total.
    lits, weights = [], []
    for t in templates:
        for x in range(2, p_max + 1):
            lits.append(production[t].ge(x))
            weights.append(1)
    thresholds = [total.ge(x) for x in range(lower + 1, max(upper, lower + 1) + 1)]
    lits += thresholds
    weights += [-1] * len(thresholds)
    # sheets - n_templates - (total - lower) <= lower - n_templates, written
    # with the bound on the right as PBEnc refuses a negative one (lower is at
    # least n_templates).
    formula.extend(PBEnc.leq(lits=lits, weights=weights, bound=lower - n_templates,
                             vpool=pool, encoding=PBType.adder).clauses)

    # Minimise the number of printed sheets: reaching total >= v pays a
    # weight that grows with v, so what is paid strictly rises with the
    # sheets printed. The weights come in about sqrt(N) groups, so stratified
    # RC2 settles a group at a time instead of one sheet per core.
    group = isqrt(max(upper - lower, 1)) + 1
    for v in range(lower + 1, upper + 1):
        formula.append([-total.ge(v)], weight=1 + (v - lower - 1) // group)

    return formula, {"production": production, "layout": layout}
