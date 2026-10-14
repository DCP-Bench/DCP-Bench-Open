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

    # printed[t][v] = items of variation v printed from template t
    #               = sheets of template t * copies of v on template t
    printed = [[model.intvar(0, ub * n_var, name=f"printed_{t}_{v}") for v in range(n_var)]
               for t in range(n_templates)]
    for t in range(n_templates):
        for v in range(n_var):
            model.times(production[t], layout[t][v], printed[t][v]).post()

    # meet demand: the items of variation v printed from all templates,
    # sum over t of production[t] * layout[t][v], are at least its demand
    # (produced[v] is that sum, so its lower bound is the demand)
    produced = [model.intvar(demand[v], n_slots * n_templates * ub, name=f"produced_{v}") for v in range(n_var)]
    for v in range(n_var):
        model.sum([printed[t][v] for t in range(n_templates)], "=", produced[v]).post()

    # total number of printed sheets (Choco minimises one variable, so it gets its own)
    total_sheets = model.intvar(n_templates, n_templates * ub, name="total_sheets")
    model.sum(production, "=", total_sheets).post()

    # Implied: every template fills all its slots, so a sheet of it carries n_slots items.
    # Each template prints n_slots * production[t] items in all, and all templates together
    # n_slots * total_sheets, which the items produced of the variations add up to. The
    # printed sheets thus cover the total demand, and what is printed above demand is
    # limited to n_slots * total_sheets - sum(demand).
    for t in range(n_templates):
        model.scalar(printed[t] + [production[t]], [1] * n_var + [-n_slots], "=", 0).post()
    model.scalar(produced + [total_sheets], [1] * n_var + [-n_slots], "=", 0).post()

    return model, {"production": production, "layout": layout}, ("minimize", total_sheets)
