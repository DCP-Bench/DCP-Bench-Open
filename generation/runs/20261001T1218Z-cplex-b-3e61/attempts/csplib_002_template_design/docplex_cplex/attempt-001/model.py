"""Template design: decide how many copies of each design variation to etch on each printing
template (every template has a fixed number of slots, all filled) and how many sheets to print
from each template, so that every variation's demand is met with as few sheets as possible.

The model reports the number of sheets printed from each template and each template's layout.
"""
from docplex.mp.model import Model


def build(instance):
    n_slots = instance["n_slots"]          # slots on a template
    n_templates = instance["n_templates"]  # number of templates
    n_var = instance["n_var"]              # number of variations
    demand = instance["demand"]            # demand per variation
    ub = max(demand)                       # the reference's upper bound on a template's production
    templates = range(n_templates)
    variations = range(n_var)

    model = Model("template_design")

    # production[i]: sheets printed from template i (the reference's domain 1..max demand).
    production = [model.integer_var(1, ub, name=f"production_{i}") for i in templates]

    # layout[i][v]: copies of variation v on template i, in the reference's domain 0..n_var.
    # The demand rule multiplies layout by production, which CPLEX refuses for two variables.
    # Each layout is therefore written in binary, layout = sum 2^k * bit[k], and each product
    # bit[k] * production is a variable tied to it by the standard four inequalities.
    n_bits = max(1, n_var.bit_length())
    bit = {(i, v, k): model.binary_var(name=f"bit_{i}_{v}_{k}")
           for i in templates for v in variations for k in range(n_bits)}
    layout_vars = [[model.integer_var(0, n_var, name=f"layout_{i}_{v}") for v in variations] for i in templates]
    for i in templates:
        for v in variations:
            model.add_constraint(layout_vars[i][v] == model.sum(2 ** k * bit[i, v, k] for k in range(n_bits)))

    made = {}
    for i in templates:
        for v in variations:
            for k in range(n_bits):
                p = model.integer_var(0, ub, name=f"made_{i}_{v}_{k}")
                b = bit[i, v, k]
                model.add_constraint(p <= ub * b)
                model.add_constraint(p >= 1 * b)
                model.add_constraint(p <= production[i] - 1 * (1 - b))
                model.add_constraint(p >= production[i] - ub * (1 - b))
                made[i, v, k] = p

    # All slots of every template are populated.
    for i in templates:
        model.add_constraint(model.sum(layout_vars[i]) == n_slots)

    # The sheets printed meet the demand of every variation: the copies of a variation over all
    # templates, times the sheets printed from each, reach its demand.
    for v in variations:
        model.add_constraint(model.sum(2 ** k * made[i, v, k] for i in templates for k in range(n_bits))
                             >= demand[v])

    # Implied, as in the reference: every template fills all its slots, so the sheets cover the
    # total demand.
    model.add_constraint(n_slots * model.sum(production) >= sum(demand))

    # Minimize the number of printed sheets.
    model.minimize(model.sum(production))

    return model, {"production": production, "layout": layout_vars}
