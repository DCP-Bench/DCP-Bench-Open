"""Template design: choose how many copies of each variation go on each printing template, and how many sheets to print from each, meeting demand with the fewest sheets."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n_slots = instance["n_slots"]
    n_templates = instance["n_templates"]
    n_var = instance["n_var"]
    demand = instance["demand"]
    templates = range(n_templates)
    variations = range(n_var)
    ub = max(demand)   # upper bound on the sheets printed from one template, as in the reference

    model = gp.Model("template_design")

    # production[i]: number of sheets printed from template i, between 1 and ub.
    production = model.addVars(templates, lb=1, ub=ub, vtype=GRB.INTEGER, name="production")

    # layout[i][v]: copies of variation v on template i, in 0..n_var as in the reference.
    # It is written in binary, layout = sum 2^k bit[k], so that the product
    # production * layout becomes a sum of binary-times-integer products, which are
    # linear; a product of two variables would drop the licence limit to 200 variables.
    n_bits = max(1, n_var.bit_length())
    bits = range(n_bits)
    bit = model.addVars(templates, variations, bits, vtype=GRB.BINARY, name="bit")
    layout = [[gp.quicksum((2 ** k) * bit[i, v, k] for k in bits) for v in variations] for i in templates]
    for i in templates:
        for v in variations:
            model.addConstr(layout[i][v] <= n_var, name=f"layout_ub[{i},{v}]")

    # sheets[i, v, k] = production[i] * bit[i, v, k], by the binary-times-integer encoding.
    sheets = model.addVars(templates, variations, bits, lb=0, ub=ub, vtype=GRB.CONTINUOUS, name="sheets")
    for i in templates:
        for v in variations:
            for k in bits:
                b, s = bit[i, v, k], sheets[i, v, k]
                model.addConstr(s <= ub * b)
                model.addConstr(s >= 1 * b)
                model.addConstr(s <= production[i] - 1 * (1 - b))
                model.addConstr(s >= production[i] - ub * (1 - b))

    # All slots of every template are populated.
    for i in templates:
        model.addConstr(gp.quicksum(layout[i][v] for v in variations) == n_slots, name=f"slots[{i}]")

    # Meet demand: the copies printed of each variation, sheets times copies per sheet
    # summed over the templates, reach its demand.
    for v in variations:
        printed = gp.quicksum((2 ** k) * sheets[i, v, k] for i in templates for k in bits)
        model.addConstr(printed >= demand[v], name=f"demand[{v}]")

    # Implied: every template fills all its slots, so the sheets cover the total demand.
    model.addConstr(n_slots * production.sum() >= sum(demand), name="total_demand")

    # Minimise the number of printed sheets.
    model.setObjective(production.sum(), GRB.MINIMIZE)

    return model, {
        "production": [production[i] for i in templates],
        "layout": layout,
    }
