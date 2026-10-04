# Cutting stock: choose how many raw rolls to cut with each given cutting
# pattern so that every ordered width is produced at least as often as it was
# ordered, using as few raw rolls as possible.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    orders = instance["orders"]
    num_patterns = instance["num_patterns"]
    num_rolls_width = instance["num_rolls_width"]  # pieces of width i in pattern j
    num_item_widths = len(orders)

    # Upper bound on each pattern's use. The reference allows 0..100. An
    # optimal plan never uses a pattern once more than needed: dropping one
    # roll cut with pattern j must leave some width i that j produces short,
    # so pattern j is used at most ceil(orders[i] / pieces of i in j) times
    # for some such i. A pattern producing nothing is never used in an
    # optimal plan. Every optimal plan lies within these bounds.
    ub = []
    for j in range(num_patterns):
        reach = [-(-max(orders[i], 0) // num_rolls_width[j][i])
                 for i in range(num_item_widths) if num_rolls_width[j][i] > 0]
        ub.append(min(100, max(reach)) if reach else 0)

    pool = IDPool()
    # patterns_used[j] is the number of raw rolls cut with pattern j. Coupled
    # encoding: the order half gives the covering sums and the objective unit
    # thresholds, the direct half the "== v" literals the runner blocks on.
    # A domain is never a single value; a bound of 0 is posted below.
    patterns_used = [Integer(f"patterns_used{j}", 0, max(ub[j], 1), encoding="coupled",
                             vpool=pool) for j in range(num_patterns)]
    # min_rolls_cut is the total number of raw rolls cut.
    total_ub = sum(ub)
    min_rolls_cut = Integer("min_rolls_cut", 0, max(total_ub, 1), encoding="coupled",
                            vpool=pool)
    engine = IntegerEngine(vars=patterns_used + [min_rolls_cut], vpool=pool)
    for j in range(num_patterns):
        if ub[j] == 0:
            engine.add_linear(patterns_used[j] <= 0)

    # For each width, the pieces cut over all patterns meet its orders.
    unmet = False
    for i in range(num_item_widths):
        terms = [num_rolls_width[j][i] * patterns_used[j]
                 for j in range(num_patterns) if num_rolls_width[j][i] != 0]
        if terms:
            engine.add_linear(sum(terms) >= orders[i])
        elif orders[i] > 0:
            # no pattern produces this width, so the order cannot be met
            unmet = True

    # The total number of raw rolls cut is the sum of the pattern uses.
    engine.add_linear(min_rolls_cut - sum(patterns_used) == 0)

    # Implied lower bounds on the rolls cut, stated so the solver does not
    # have to rediscover them. A roll cut with any pattern yields at most
    # most_pieces[i] pieces of width i, so meeting orders[i] takes at least
    # ceil(orders[i] / most_pieces[i]) rolls. And a roll yields at most
    # widest units of ordered width (the widest pattern's total), while the
    # orders need sum(orders[i] * widths[i]) units, so at least that sum over
    # widest rolls are cut.
    widths = instance["widths"]
    lower = 0
    for i in range(num_item_widths):
        most_pieces = max(num_rolls_width[j][i] for j in range(num_patterns))
        if orders[i] > 0 and most_pieces > 0:
            lower = max(lower, -(-orders[i] // most_pieces))
    widest = max(sum(num_rolls_width[j][i] * widths[i] for i in range(num_item_widths))
                 for j in range(num_patterns))
    if widest > 0 and min(widths) > 0:
        need = sum(max(orders[i], 0) * widths[i] for i in range(num_item_widths))
        lower = max(lower, -(-need // widest))
    lower = min(lower, total_ub)
    engine.add_linear(min_rolls_cut >= lower)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)
    if unmet:
        contradiction = pool.id("unmet order")
        formula.append([contradiction])
        formula.append([-contradiction])

    # Minimise the raw rolls cut: every roll above the implied lower bound pays
    # 1, one weight-1 soft clause per threshold of min_rolls_cut. Stated on
    # the total rather than on each pattern's use, RC2 raises a single lower
    # bound one roll at a time.
    for v in range(lower + 1, total_ub + 1):
        formula.append([-min_rolls_cut.ge(v)], weight=1)

    return formula, {"patterns_used": patterns_used, "min_rolls_cut": min_rolls_cut}
