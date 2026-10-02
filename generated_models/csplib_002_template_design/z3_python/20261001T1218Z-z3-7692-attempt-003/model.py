# Template design: decide how many sheets to print from each template, and how many copies
# of each variation to put on each template, so that every variation's demand is met, every
# slot of a template is used, and as few sheets as possible are printed.
import z3


def build(instance):
    n_slots = instance["n_slots"]          # slots on a template
    n_templates = instance["n_templates"]  # number of templates
    n_var = instance["n_var"]              # number of variations
    demand = instance["demand"]            # demand of each variation
    ub = max(demand)                       # upper bound on the sheets printed per template

    # production[t] is the number of sheets printed from template t.
    production = [z3.Int(f"production_{t}") for t in range(n_templates)]
    # layout[t][v] is the number of copies of variation v on template t, between 0 and n_var
    # (the reference's domain).
    layout = [[z3.Int(f"layout_{t}_{v}") for v in range(n_var)] for t in range(n_templates)]
    # printed[v] is the number of copies of variation v printed over all the sheets.
    printed = [z3.Int(f"printed_{v}") for v in range(n_var)]
    total_sheets = z3.Sum(production)

    solver = z3.Solver()

    for t in range(n_templates):
        solver.add(production[t] >= 1, production[t] <= ub)
        for v in range(n_var):
            solver.add(layout[t][v] >= 0, layout[t][v] <= n_var)

    # All the slots of every template are populated.
    for t in range(n_templates):
        solver.add(z3.Sum(layout[t]) == n_slots)

    # The copies of variation v printed are, for each template, its sheets times the copies of v
    # on it. That is a product of two variables; nonlinear products are slow in Z3, so it is
    # written as a sum over the possible values k of layout[t][v] of "k times production[t]",
    # which only multiplies by constants.
    for v in range(n_var):
        solver.add(printed[v] == z3.Sum([z3.If(layout[t][v] == k, k * production[t], 0)
                                         for t in range(n_templates)
                                         for k in range(1, n_var + 1)]))

    # Meet the demand: at least as many copies of each variation are printed as demanded.
    for v in range(n_var):
        solver.add(printed[v] >= demand[v])

    # Implied: every sheet carries n_slots copies, so the copies printed in total are
    # n_slots times the sheets. Together with the demands, the sheets cover the total
    # demand, and the copies printed above the demand of a variation add up to
    # n_slots * sheets - total demand, which bounds each one of them. Z3 cannot derive this
    # from the product-free form above.
    solver.add(z3.Sum(printed) == n_slots * total_sheets)
    solver.add(n_slots * total_sheets >= sum(demand))

    # Minimize the number of printed sheets.
    return solver, {"production": production, "layout": layout}, ("minimize", total_sheets)
