# Template design (CSPLib 2): a printing firm orders several design variations. Choose how many
# templates to use (given), how many copies of each variation go on each template, and how many
# sheets are printed from each template, so that every variation's demand is met and as few
# sheets as possible are printed in total.
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

    # The demand constraint multiplies two variables (sheets times copies). Exact is linear, so the
    # product is built from 0/1 variables: has[t][v][k] = 1 when layout[t][v] == k, and
    # sheets[t][v][k] = production[t] if layout[t][v] == k, else 0. Then the printed copies of
    # variation v from template t are sum_k k * sheets[t][v][k].
    has = {}
    sheets = {}
    for t in range(n_templates):
        for v in range(n_var):
            for k in range(max_copies + 1):
                has[t, v, k] = f"has_{t}_{v}_{k}"
                solver.addVariable(has[t, v, k], 0, 1)
            # layout[t][v] takes exactly one value k
            solver.addConstraint([(1, has[t, v, k]) for k in range(max_copies + 1)],
                                 True, 1, True, 1)
            solver.addConstraint([(k, has[t, v, k]) for k in range(1, max_copies + 1)]
                                 + [(-1, layout[t][v])], True, 0, True, 0)
            for k in range(1, max_copies + 1):
                sheets[t, v, k] = f"sheets_{t}_{v}_{k}"
                solver.addVariable(sheets[t, v, k], 0, ub)
                # sheets <= ub * has, sheets <= production, sheets >= production - ub * (1 - has)
                solver.addConstraint([(1, sheets[t, v, k]), (-ub, has[t, v, k])],
                                     False, 0, True, 0)
                solver.addConstraint([(1, sheets[t, v, k]), (-1, production[t])],
                                     False, 0, True, 0)
                solver.addConstraint([(1, sheets[t, v, k]), (-1, production[t]),
                                      (-ub, has[t, v, k])], True, -ub)

    # meet demand: the copies of each variation printed over all templates cover its demand
    for v in range(n_var):
        solver.addConstraint([(k, sheets[t, v, k]) for t in range(n_templates)
                              for k in range(1, max_copies + 1)], True, demand[v])

    # implied: every template fills all its slots, so the sheets cover the total demand
    solver.addConstraint([(n_slots, name) for name in production], True, sum(demand))

    # minimise the number of printed sheets
    return (solver, {"production": production, "layout": layout},
            ("minimize", [(1, name) for name in production]))
