# csplib_002_template_design: template design for printing variations from mother sheets.
# Each template has n_slots slots, each slot carries one variation, and each template is
# printed production[t] sheets. Every variation's demand must be covered by the copies
# printed over all templates. Minimise the total number of printed sheets.
import cvc5.pythonic as cz


def build(instance):
    n_slots = instance["n_slots"]
    n_templates = instance["n_templates"]
    n_var = instance["n_var"]
    demand = instance["demand"]
    max_demand = max(demand)
    total_demand = sum(demand)

    solver = cz.SolverFor("QF_LIA")

    # layout[t][v]: number of slots of template t that carry variation v
    layout = [[cz.Int(f"layout_{t}_{v}") for v in range(n_var)] for t in range(n_templates)]
    # production[t]: number of sheets printed from template t
    production = [cz.Int(f"production_{t}") for t in range(n_templates)]
    # copies[t][v]: copies of variation v printed from template t (layout times sheets)
    copies = [[cz.Int(f"copies_{t}_{v}") for v in range(n_var)] for t in range(n_templates)]

    cons = []

    # Each template has exactly n_slots slots, and each slot holds one variation.
    for t in range(n_templates):
        for v in range(n_var):
            cons.append(layout[t][v] >= 0)
            cons.append(layout[t][v] <= n_slots)
        cons.append(cz.Sum(layout[t]) == n_slots)

    # Sheets printed from a template are between 0 and the largest demand.
    for t in range(n_templates):
        cons.append(production[t] >= 0)
        cons.append(production[t] <= max_demand)

    # Copies of variation v from template t are layout[t][v] times production[t].
    # Each layout value is a case split, so the product stays linear.
    for t in range(n_templates):
        for v in range(n_var):
            cons.append(copies[t][v] >= 0)
            cons.append(copies[t][v] <= n_slots * max_demand)
            for k in range(n_slots + 1):
                cons.append(cz.Implies(layout[t][v] == k, copies[t][v] == k * production[t]))

    # Every variation's demand is covered by the copies printed over all templates.
    for v in range(n_var):
        cons.append(cz.Sum([copies[t][v] for t in range(n_templates)]) >= demand[v])

    # Derived totals: each template prints n_slots copies per sheet, so the copies of
    # all variations equal n_slots times the sheets, which must cover the total demand.
    for t in range(n_templates):
        cons.append(cz.Sum(copies[t]) == n_slots * production[t])
    cons.append(n_slots * cz.Sum(production) >= total_demand)

    # The copies of all variations sum to n_slots times the sheets, and every other
    # variation is printed at least its demand, so no variation can exceed that remainder.
    for v in range(n_var):
        cons.append(
            cz.Sum([copies[t][v] for t in range(n_templates)])
            <= n_slots * cz.Sum(production) - (total_demand - demand[v])
        )

    outputs = {"layout": layout, "production": production}
    objective = cz.Sum(production)
    solver.add(*cons)
    return solver, outputs, ("minimize", objective)
