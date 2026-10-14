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
    copies = range(n_var + 1)   # copies of a variation on a template, 0..n_var as in the reference
    ub = max(demand)            # upper bound on the sheets printed from one template, as in the reference

    model = gp.Model("template_design")
    # The bound n_slots * sheets >= total demand usually already meets the optimum,
    # so the search is mostly for a feasible schedule at that bound.
    model.Params.MIPFocus = 1

    # production[i]: number of sheets printed from template i, between 1 and ub.
    production = model.addVars(templates, lb=1, ub=ub, vtype=GRB.INTEGER, name="production")

    # has[i, v, c] is 1 when template i carries c copies of variation v.
    has = model.addVars(templates, variations, copies, vtype=GRB.BINARY, name="has")
    for i in templates:
        for v in variations:
            model.addConstr(has.sum(i, v, "*") == 1, name=f"one_count[{i},{v}]")
    layout = [[gp.quicksum(c * has[i, v, c] for c in copies) for v in variations] for i in templates]

    # sheets[i, v, c] = production[i] * has[i, v, c]: the sheets of template i, counted
    # under the number of copies of v it carries. Splitting production[i] this way
    # (sheets summed over c equals production[i]) keeps production * layout linear,
    # which a product of two variables would not be (the licence then allows only
    # 200 variables), and gives a much tighter relaxation than big-M products alone.
    sheets = model.addVars(templates, variations, copies, lb=0, ub=ub, vtype=GRB.CONTINUOUS, name="sheets")
    for i in templates:
        for v in variations:
            model.addConstr(sheets.sum(i, v, "*") == production[i], name=f"split[{i},{v}]")
            for c in copies:
                model.addConstr(sheets[i, v, c] <= ub * has[i, v, c], name=f"only_if[{i},{v},{c}]")

    # All slots of every template are populated; the second line is the same fact
    # counted per printed sheet.
    for i in templates:
        model.addConstr(gp.quicksum(layout[i][v] for v in variations) == n_slots, name=f"slots[{i}]")
        model.addConstr(gp.quicksum(c * sheets[i, v, c] for v in variations for c in copies)
                        == n_slots * production[i], name=f"slots_per_sheet[{i}]")

    # Meet demand: the copies printed of each variation, sheets times copies per sheet
    # summed over the templates, reach its demand.
    for v in variations:
        model.addConstr(gp.quicksum(c * sheets[i, v, c] for i in templates for c in copies) >= demand[v],
                        name=f"demand[{v}]")

    # Implied: every template fills all its slots, so the sheets cover the total demand.
    model.addConstr(n_slots * production.sum() >= sum(demand), name="total_demand")

    # Minimise the number of printed sheets.
    model.setObjective(production.sum(), GRB.MINIMIZE)

    return model, {
        "production": [production[i] for i in templates],
        "layout": layout,
    }
