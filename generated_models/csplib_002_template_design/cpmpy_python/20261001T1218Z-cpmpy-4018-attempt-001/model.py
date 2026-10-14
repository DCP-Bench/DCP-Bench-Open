# Template design: a printer makes several variations of a carton on mother sheets. Each sheet is
# printed from a template with a fixed number of slots, each slot holding one variation. Choose
# the contents of n_templates templates and how many sheets to print from each, so that every
# variation reaches its demand with as few printed sheets as possible.
import cpmpy as cp


def build(instance):
    n_slots = instance["n_slots"]          # slots on a template
    n_templates = instance["n_templates"]  # number of different templates
    n_var = instance["n_var"]              # number of variations
    demand = instance["demand"]            # copies wanted of each variation

    # production[t] = sheets printed from template t. At least one sheet is printed per template,
    # and no template needs more sheets than the largest single demand: one sheet gives at least
    # one copy of a variation it carries.
    production = cp.intvar(1, max(demand), shape=(n_templates,), name="production")

    # layout[t, v] = slots of template t that hold variation v. The number of copies of one
    # variation on a template is bounded by n_var, as in the problem definition.
    layout = cp.intvar(0, n_var, shape=(n_templates, n_var), name="layout")

    model = cp.Model()

    # Every slot of every template holds a variation.
    for t in range(n_templates):
        model += cp.sum(layout[t, :]) == n_slots

    # Demand is met: the copies of variation v over all printed sheets, summed over templates,
    # are at least demand[v].
    for v in range(n_var):
        model += cp.sum([production[t] * layout[t, v] for t in range(n_templates)]) >= demand[v]

    # Implied constraint: all slots are filled, so n_slots copies come off each sheet and the
    # sheets together must cover the total demand. It helps the solver bound the objective.
    model += n_slots * cp.sum(production) >= sum(demand)

    # Minimise the total number of printed sheets.
    model.minimize(cp.sum(production))

    return model, {"layout": layout, "production": production}
