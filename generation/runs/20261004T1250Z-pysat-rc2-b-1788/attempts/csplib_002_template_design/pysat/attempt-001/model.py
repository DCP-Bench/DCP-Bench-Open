# Template design (CSPLib 2): fill the slots of each printing template with
# copies of the design variations and choose how many sheets to print from
# each template, so that every variation's demand is met with as few printed
# sheets as possible.
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
    # Sheets per template lie in 1..max(demand) and copies of a variation on
    # a template in 0..n_var, the domains the reference declares.
    ub = max(max(demand), 2)   # widened to 2 values at least, see below

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
        for v in range(max(demand) + 1, ub + 1):
            formula.append([-production[t].equals(v)])
        if n_var < 1:
            for v in variations:
                formula.append([-layout[t][v].equals(1)])

    # The products production[t] * layout[t][v] are not linear, so both
    # factors are spelled out in binary digits, value by value, and each
    # product is a weighted sum of digit pairs: the digit pair (b, c) is
    # worth 2^(b + c) sheets' worth of copies. pair[t][v][b][c] can only be
    # true when both digits are 1, which is all a lower bound on the copies
    # needs.
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
    # sum over t of production[t] * layout[t][v], reach its demand. Adder
    # encoding: the weights are powers of two up to 2^14, where a BDD would
    # be large.
    for v in variations:
        lits, weights = [], []
        for t in templates:
            for b, pb in enumerate(prod_bits[t]):
                for c, lb in enumerate(layout_bits[t][v]):
                    pair = pool.id(("pair", t, v, b, c))
                    formula.append([-pair, pb])
                    formula.append([-pair, lb])
                    lits.append(pair)
                    weights.append(1 << (b + c))
        formula.extend(PBEnc.geq(lits=lits, weights=weights, bound=demand[v], vpool=pool,
                                 encoding=PBType.adder).clauses)

    # Implied (stated in the reference): every template fills all its slots,
    # so the sheets cover the total demand.
    formula.extend(PBEnc.geq(lits=[pb for t in templates for pb in prod_bits[t]],
                             weights=[n_slots << b for t in templates
                                      for b in range(len(prod_bits[t]))],
                             bound=sum(demand), vpool=pool, encoding=PBType.adder).clauses)

    # Minimise the number of printed sheets: binary digit b of a template's
    # sheet count pays 2^b.
    for t in templates:
        for b, pb in enumerate(prod_bits[t]):
            formula.append([-pb], weight=1 << b)

    return formula, {"production": production, "layout": layout}
