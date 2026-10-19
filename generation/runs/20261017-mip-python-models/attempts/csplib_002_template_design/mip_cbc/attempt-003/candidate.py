# Template design (CSPLib 002): a printing firm prints mother sheets from templates.
# Each template has n_slots slots, each slot holds one copy of one design variation.
# Decide the layout of each of the n_templates templates (how many copies of each
# variation it carries) and how many sheets to print from each template, so that every
# variation's demand is met, minimising the total number of printed sheets.
import itertools

import mip

# Up to this many copy-count combinations per variation, the product of layout and production
# is linearised per combination over all templates (a tighter relaxation); above it, per
# template and copy count.
MAX_COMBINATIONS = 200


def combination_layout(m, production, n_slots, demand, T, V, max_d):
    # For each variation, one binary per combination of copy counts over the templates
    # (copies[t] copies of the variation on template t). For a template with copies[t] > 0,
    # sheets is the part of its production counted towards this variation under that
    # combination: zero unless the combination is chosen, and never more than
    # ceil(demand / copies[t]), since more sheets of that template alone already meet it.
    layout = [[[] for v in V] for t in T]
    for v in V:
        choices = []
        counted = [[] for t in T]
        for copies in itertools.product(range(n_slots + 1), repeat=len(T)):
            if sum(copies) == 0:
                continue  # a variation with no copy anywhere cannot meet a positive demand
            pick = m.add_var(f"pick_{v}_{'_'.join(map(str, copies))}", var_type=mip.BINARY)
            choices.append(pick)
            printed = []
            for t in T:
                layout[t][v].append(copies[t] * pick)
                if copies[t] == 0:
                    continue
                cap = min(max_d, -(-demand[v] // copies[t]))
                sheets = m.add_var(lb=0, ub=cap)
                m += sheets <= cap * pick
                counted[t].append(sheets)
                printed.append(copies[t] * sheets)
            # The copies printed of the variation under this combination meet its demand
            m += mip.xsum(printed) >= demand[v] * pick
        # Each variation has exactly one number of copies on each template
        m += mip.xsum(choices) == 1
        # The sheets counted for a variation never exceed what each template prints
        for t in T:
            m += mip.xsum(counted[t]) <= production[t]
    return [[mip.xsum(layout[t][v]) for v in V] for t in T]


def per_template_layout(m, production, n_slots, demand, T, V, max_d):
    # has[t][v][k] = 1 when template t carries exactly k copies of variation v.
    # sheets[t][v][k] is the part of template t's production counted towards variation v
    # when it carries k copies: zero unless it does, at most ceil(demand / k).
    has = [[[m.add_var(f"has_{t}_{v}_{k}", var_type=mip.BINARY) for k in range(n_slots + 1)]
            for v in V] for t in T]
    sheets = {}
    for t in T:
        for v in V:
            # Each variation has exactly one number of copies on each template
            m += mip.xsum(has[t][v]) == 1
            for k in range(1, n_slots + 1):
                cap = min(max_d, -(-demand[v] // k))
                sheets[t, v, k] = m.add_var(lb=0, ub=cap)
                m += sheets[t, v, k] <= cap * has[t][v][k]
            # The sheets counted for a variation never exceed what the template prints
            m += mip.xsum(sheets[t, v, k] for k in range(1, n_slots + 1)) <= production[t]
    # The copies printed of each variation over all templates meet its demand
    for v in V:
        m += mip.xsum(k * sheets[t, v, k] for t in T for k in range(1, n_slots + 1)) >= demand[v]
    # Implied: a template printed production[t] times carries n_slots * production[t] copies
    for t in T:
        m += mip.xsum(k * sheets[t, v, k] for v in V for k in range(1, n_slots + 1)) \
            <= n_slots * production[t]
    return [[mip.xsum(k * has[t][v][k] for k in range(n_slots + 1)) for v in V] for t in T]


def build(instance):
    n_slots = instance["n_slots"]
    n_templates = instance["n_templates"]
    n_var = instance["n_var"]
    demand = instance["demand"]
    max_d = max(demand)
    T, V = range(n_templates), range(n_var)

    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Number of sheets printed from each template
    production = [m.add_var(f"production_{t}", lb=1, ub=max_d, var_type=mip.INTEGER) for t in T]

    # Copies of each variation on each template, with the demand of every variation met
    if (n_slots + 1) ** n_templates <= MAX_COMBINATIONS:
        layout = combination_layout(m, production, n_slots, demand, T, V, max_d)
    else:
        layout = per_template_layout(m, production, n_slots, demand, T, V, max_d)

    # Every slot of a template holds one variation: the copies on a template fill its n_slots slots
    for t in T:
        m += mip.xsum(layout[t][v] for v in V) == n_slots

    # Implied by the above: every sheet carries n_slots copies, so the sheets printed carry at
    # least the total demand; the number of sheets is an integer, so round up
    m += mip.xsum(production) >= -(-sum(demand) // n_slots)

    # Minimise the total number of printed sheets
    m.objective = mip.xsum(production)

    return m, {"layout": layout, "production": production}
