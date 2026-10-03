# Template design: a printing firm must fill orders for several variations of a product
# from sheets printed with templates. Decide how many sheets to print from each template
# and how many copies of each variation to put on each template (every template has the
# same number of slots), so that the demand of every variation is met with as few printed
# sheets as possible.
from pychoco.model import Model


def build(instance):
    n_slots = instance["n_slots"]  # slots on a template
    n_templates = instance["n_templates"]  # number of templates
    n_var = instance["n_var"]  # number of variations
    demand = instance["demand"]  # demand[v] = items wanted of variation v

    ub = max(demand)  # upper bound for the production of one template

    model = Model()

    # production[t] = number of sheets printed from template t
    production = [model.intvar(1, ub, name=f"production_{t}") for t in range(n_templates)]
    # layout[t][v] = copies of variation v on template t
    layout = [[model.intvar(0, n_var, name=f"layout_{t}_{v}") for v in range(n_var)]
              for t in range(n_templates)]

    # all slots are populated in a template
    for t in range(n_templates):
        model.sum(layout[t], "=", n_slots).post()

    # meet demand: the items of variation v printed from all templates,
    # sum over t of production[t] * layout[t][v], are at least its demand.
    # printed[t][v] = items of variation v printed from template t
    printed = [[model.intvar(0, ub * n_var, name=f"printed_{t}_{v}") for v in range(n_var)]
               for t in range(n_templates)]
    for t in range(n_templates):
        for v in range(n_var):
            model.times(production[t], layout[t][v], printed[t][v]).post()
    for v in range(n_var):
        model.sum([printed[t][v] for t in range(n_templates)], ">=", demand[v]).post()

    # implied: every template fills all its slots, so the printed sheets cover the total demand
    model.scalar(production, [n_slots] * n_templates, ">=", sum(demand)).post()

    # total number of printed sheets (Choco minimises one variable, so it gets its own)
    total_sheets = model.intvar(n_templates, n_templates * ub, name="total_sheets")
    model.sum(production, "=", total_sheets).post()

    return model, {"production": production, "layout": layout}, ("minimize", total_sheets)
