# csplib_002_template_design: choose the printing templates (how many, and for each
# one how many copies of each design variation it carries) and how many sheets to
# print from each template, so that every variation's demand is met while the total
# number of printed sheets is minimised.
import cvc5.pythonic as cz


def build(instance):
    n_slots = instance["n_slots"]  # designs that fit on one template
    n_templates = instance["n_templates"]
    n_var = instance["n_var"]  # design variations
    demand = instance["demand"]  # copies needed of each variation
    # A template never needs to print more sheets than the largest single demand:
    # with a copy of v on the template, that many sheets already cover v, and a
    # template with no copies needs no sheets. So this bound keeps the optimum.
    max_sheets = max(demand)
    total_demand = sum(demand)

    # layout[t][v]: number of copies of variation v etched on template t
    layout = [[cz.Int(f"layout_{t}_{v}") for v in range(n_var)] for t in range(n_templates)]
    # production[t]: number of sheets printed from template t
    production = [cz.Int(f"production_{t}") for t in range(n_templates)]
    # printed[t][v]: copies of variation v obtained from template t, layout[t][v] * production[t]
    printed = [[cz.Int(f"printed_{t}_{v}") for v in range(n_var)] for t in range(n_templates)]

    constraints = []

    # domains of the template layout and of the sheet counts
    for t in range(n_templates):
        constraints.append(production[t] >= 0)
        constraints.append(production[t] <= max_sheets)
        for v in range(n_var):
            constraints.append(layout[t][v] >= 0)
            constraints.append(layout[t][v] <= n_slots)

    # the design copies on one template fit in its n_slots slots
    for t in range(n_templates):
        constraints.append(cz.Sum(layout[t]) <= n_slots)

    # printed = layout * production as one term: the layout is bounded by n_slots,
    # so the product is a sum of If terms, each a constant times production
    # (no product of two unknowns, which the solver would have to linearise)
    for t in range(n_templates):
        for v in range(n_var):
            constraints.append(
                printed[t][v] == cz.Sum([cz.If(layout[t][v] == k, k * production[t], 0) for k in range(1, n_slots + 1)])
            )
        # implied by the slot limit: the copies printed from a template are at most
        # n_slots per sheet (redundant, but it tightens the search)
        constraints.append(cz.Sum(printed[t]) <= n_slots * production[t])

    # every variation's demand is met by the copies printed over all templates
    for v in range(n_var):
        constraints.append(cz.Sum([printed[t][v] for t in range(n_templates)]) >= demand[v])

    # implied by the demand and the slot limit: the sheets printed must cover all
    # demanded copies at n_slots copies per sheet (redundant lower bound on the sheets)
    constraints.append(n_slots * cz.Sum(production) >= total_demand)

    # objective: the total number of printed sheets
    objective = cz.Sum(production)

    outputs = {"layout": layout, "production": production}
    return constraints, outputs, ("minimize", objective)
