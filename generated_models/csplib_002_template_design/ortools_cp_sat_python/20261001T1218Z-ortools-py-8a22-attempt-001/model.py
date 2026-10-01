# Template design: choose the layout of printing templates and how many sheets to print
# from each, so every variation's demand is met with as few printed sheets as possible.
from ortools.sat.python import cp_model


def build(instance):
    n_slots = instance["n_slots"]          # slots (variation copies) on one template
    n_templates = instance["n_templates"]  # number of distinct templates to produce
    n_var = instance["n_var"]              # number of variations of the product
    demand = instance["demand"]            # demand[v] = sheets needed of variation v

    # Upper bound on the sheets printed from one template, as the problem definition sets it:
    # the largest single demand.
    ub = max(demand)

    model = cp_model.CpModel()

    # production[i] = number of sheets printed from template i (at least 1).
    production = [model.new_int_var(1, ub, f"production_{i}") for i in range(n_templates)]
    # layout[i][v] = number of copies of variation v on template i (at most n_var, the
    # problem's own domain; the slot count below already limits it further).
    layout = [[model.new_int_var(0, n_var, f"layout_{i}_{v}") for v in range(n_var)]
              for i in range(n_templates)]

    # Every slot of every template is populated.
    for i in range(n_templates):
        model.add(sum(layout[i]) == n_slots)

    # Meet demand: the copies of variation v printed over all templates (sheets of the template
    # times copies of v on it) cover demand[v]. The product of two variables needs a helper
    # variable per (template, variation), tied with a multiplication constraint.
    printed = [[model.new_int_var(0, ub * n_var, f"printed_{i}_{v}") for v in range(n_var)]
               for i in range(n_templates)]
    for i in range(n_templates):
        for v in range(n_var):
            model.add_multiplication_equality(printed[i][v], [production[i], layout[i][v]])
    for v in range(n_var):
        model.add(sum(printed[i][v] for i in range(n_templates)) >= demand[v])

    # Implied (it is also in the reference): every template fills all its slots, so the
    # printed sheets together carry n_slots copies each and must cover the total demand.
    model.add(n_slots * sum(production) >= sum(demand))

    # Minimise the number of printed sheets.
    model.minimize(sum(production))
    return model, {"production": production, "layout": layout}
