# Template design: choose printing templates and the copies of each design variation
# on each template, so that every variation's demand is met using the fewest printed sheets.
from pyscipopt import Model, quicksum


def build(instance):
    n_slots = instance["n_slots"]          # design slots on one template
    n_templates = instance["n_templates"]  # number of distinct templates to produce
    n_var = instance["n_var"]              # number of design variations
    demand = instance["demand"]            # copies required of each variation

    m = Model()

    # layout[t][v]: copies of variation v etched on template t
    layout = [[m.addVar(name=f"layout_{t}_{v}", vtype="I", lb=0, ub=n_slots)
               for v in range(n_var)] for t in range(n_templates)]
    # production[t]: number of sheets printed from template t
    # A template never needs more sheets than the largest demand: beyond that,
    # some variation on it is over-supplied and a sheet can be removed.
    max_sheets = max(demand)
    production = [m.addVar(name=f"production_{t}", vtype="I", lb=0, ub=max_sheets)
                  for t in range(n_templates)]

    # a template holds at most n_slots variations
    for t in range(n_templates):
        # the design slots on a template are limited to n_slots
        m.addCons(quicksum(layout[t][v] for v in range(n_var)) <= n_slots)

    # the copies printed of each variation must cover its demand
    # (sheets from each template times the copies of that variation on it)
    for v in range(n_var):
        m.addCons(quicksum(production[t] * layout[t][v] for t in range(n_templates))
                  >= demand[v])

    # minimise the total number of printed sheets
    m.setObjective(quicksum(production), "minimize")

    return m, {"layout": layout, "production": production}
