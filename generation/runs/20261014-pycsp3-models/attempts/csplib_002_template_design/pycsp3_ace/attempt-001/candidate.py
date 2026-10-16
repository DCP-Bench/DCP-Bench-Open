from pycsp3 import *

# Template design: a mother sheet is printed from one of several templates. Each
# template holds several variations, and it can hold at most n_slots of them.

demand = data.demand
n_slots = data.n_slots
n_templates = data.n_templates
n_var = data.n_var

# layout[t][v] is the number of copies of variation v on template t
layout = VarArray(size=[n_templates, n_var], dom=range(0, n_slots + 1))
# production[t] is the number of sheets printed from template t
production = VarArray(size=n_templates, dom=range(0, max(demand) + 1))

satisfy(
    # a template has room for at most n_slots variations
    [Sum(layout[t]) <= n_slots for t in range(n_templates)],

    # the copies printed from all templates cover the demand for each variation
    [Sum(layout[t][v] * production[t] for t in range(n_templates)) >= demand[v] for v in range(n_var)],

    # each sheet holds at most n_slots copies, so the sheets must cover the total demand
    Sum(production) * n_slots >= sum(demand),

    # the templates can be listed in any order, so order them by their rows
    LexIncreasing([[production[t]] + list(layout[t]) for t in range(n_templates)]),
)

# minimise the total number of printed sheets
minimize(Sum(production))
