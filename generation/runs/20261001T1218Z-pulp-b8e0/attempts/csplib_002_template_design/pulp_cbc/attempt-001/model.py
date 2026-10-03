"""Template design: a printing firm prints several variations of a product from templates.
Each template (a plate that prints one mother sheet) has a fixed number of slots, and each slot
carries one of the variations. Decide how many sheets are printed from each template and how
many slots of each variation each template has, so that every variation is printed at least as
often as it is demanded and the total number of printed sheets is as small as possible.

The model reports the number of sheets printed from each template and the layout of the
templates (the number of slots of each variation on each template).
"""
import pulp


def build(instance):
    n_slots = instance["n_slots"]  # slots on a template
    n_templates = instance["n_templates"]  # number of templates
    n_var = instance["n_var"]  # number of variations
    demand = instance["demand"]  # demand per variation
    ub = max(demand)  # upper bound for the sheets printed from a template (as in the reference)

    problem = pulp.LpProblem("template_design", pulp.LpMinimize)

    # production[t] = number of sheets printed from template t
    production = [pulp.LpVariable(f"production_{t}", 1, ub, cat="Integer")
                  for t in range(n_templates)]

    # layout[t][v] = number of slots of variation v on template t. A variation takes at most
    # n_var slots by the reference's bound and at most n_slots slots (the template has no more).
    most = min(n_var, n_slots)
    layout = [[pulp.LpVariable(f"layout_{t}_{v}", 0, most, cat="Integer") for v in range(n_var)]
              for t in range(n_templates)]

    # all slots of a template are populated
    for t in range(n_templates):
        problem += pulp.lpSum(layout[t]) == n_slots

    # The number of copies of variation v printed from template t is production[t] * layout[t][v],
    # a product of two variables. layout is written as a choice among its values,
    # has[t][v][k] = 1 if the template has k slots of the variation, and production is split over
    # the choices: sheets[t][v][k] is production[t] if has[t][v][k] = 1 and 0 otherwise. Then the
    # copies are the sum of k * sheets[t][v][k].
    has = pulp.LpVariable.dicts("has", (range(n_templates), range(n_var), range(most + 1)),
                                cat="Binary")
    sheets = pulp.LpVariable.dicts("sheets", (range(n_templates), range(n_var), range(most + 1)),
                                   0, ub)
    for t in range(n_templates):
        for v in range(n_var):
            problem += pulp.lpSum(has[t][v][k] for k in range(most + 1)) == 1
            problem += layout[t][v] == pulp.lpSum(k * has[t][v][k] for k in range(most + 1))
            problem += pulp.lpSum(sheets[t][v][k] for k in range(most + 1)) == production[t]
            for k in range(most + 1):
                problem += sheets[t][v][k] <= ub * has[t][v][k]

    # the demand of every variation is met
    for v in range(n_var):
        problem += pulp.lpSum(k * sheets[t][v][k]
                              for t in range(n_templates) for k in range(most + 1)) >= demand[v]

    # Implied (as in the reference): every template fills all its slots, so the printed sheets
    # have room for the total demand.
    problem += n_slots * pulp.lpSum(production) >= sum(demand)

    # minimise the number of printed sheets
    problem += pulp.lpSum(production)

    return problem, {"production": production, "layout": layout}
