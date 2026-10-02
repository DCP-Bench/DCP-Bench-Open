# Template design (CSPLib 2): a printing firm orders several design variations. Choose how many
# copies of each variation go on each template (every template has n_slots slots, all used) and how
# many sheets are printed from each template, so that every variation's demand is met and as few
# sheets as possible are printed in total.
from itertools import product

from exact import Exact


def build(instance):
    n_slots = instance["n_slots"]  # slots on a template
    n_templates = instance["n_templates"]  # number of templates
    n_var = instance["n_var"]  # number of different variations
    demand = instance["demand"]  # demand per variation

    ub = max(demand)  # upper bound for the sheets printed from one template, as in the reference
    # copies of one variation on a template: the reference allows 0..n_var, but a template has
    # only n_slots slots, so no more than n_slots copies fit
    max_copies = min(n_var, n_slots)
    max_printed = max_copies * n_templates * ub  # most copies of one variation that can be printed

    solver = Exact()

    # production[t] = sheets printed from template t
    production = [f"production_{t}" for t in range(n_templates)]
    for name in production:
        solver.addVariable(name, 1, ub)

    # layout[t][v] = copies of variation v on template t
    layout = [[f"layout_{t}_{v}" for v in range(n_var)] for t in range(n_templates)]
    for t in range(n_templates):
        for v in range(n_var):
            solver.addVariable(layout[t][v], 0, max_copies)

    # all slots are populated in a template
    for t in range(n_templates):
        solver.addConstraint([(1, name) for name in layout[t]], True, n_slots, True, n_slots)

    # printed[v] = copies of variation v printed over all templates, at least its demand (meet
    # demand). It equals the sum over templates of production[t] * layout[t][v], a product of two
    # variables, which Exact cannot do directly. Instead, for each variation v the numbers of copies
    # on the templates are chosen as a whole: pick[v][k] = 1 when the copies of variation v on
    # templates 0..T-1 are the vector c = (c_0, ..., c_{T-1}). Once c is chosen its entries are
    # constants, so printed[v] = c_0 * production[0] + ... + c_{T-1} * production[T-1] is linear.
    printed = [f"printed_{v}" for v in range(n_var)]
    vectors = list(product(range(max_copies + 1), repeat=n_templates))
    pick = [[f"pick_{v}_{k}" for k in range(len(vectors))] for v in range(n_var)]
    for v in range(n_var):
        solver.addVariable(printed[v], demand[v], max_printed)
        for name in pick[v]:
            solver.addVariable(name, 0, 1)
        # exactly one vector of copies is chosen for variation v
        solver.addConstraint([(1, name) for name in pick[v]], True, 1, True, 1)
        # layout[t][v] is the t-th entry of the chosen vector
        for t in range(n_templates):
            solver.addConstraint([(c[t], pick[v][k]) for k, c in enumerate(vectors) if c[t]]
                                 + [(-1, layout[t][v])], True, 0, True, 0)
        # printed[v] equals c . production for the chosen vector c (big-M relaxes it otherwise)
        for k, c in enumerate(vectors):
            dot = [(-c[t], production[t]) for t in range(n_templates) if c[t]]
            solver.addConstraint([(1, printed[v])] + dot + [(max_printed, pick[v][k])],
                                 False, 0, True, max_printed)
            solver.addConstraint([(1, printed[v])] + dot + [(-max_printed, pick[v][k])],
                                 True, -max_printed)

    # implied: every template fills all its slots, so n_slots copies are printed per sheet and the
    # copies printed over all variations are exactly n_slots times the number of sheets; with the
    # demands this bounds how much can be printed beyond the demand
    solver.addConstraint([(1, name) for name in printed] + [(-n_slots, name) for name in production],
                         True, 0, True, 0)
    # implied: every template fills all its slots, so the sheets cover the total demand
    solver.addConstraint([(n_slots, name) for name in production], True, sum(demand))

    # minimise the number of printed sheets
    return (solver, {"production": production, "layout": layout},
            ("minimize", [(1, name) for name in production]))
