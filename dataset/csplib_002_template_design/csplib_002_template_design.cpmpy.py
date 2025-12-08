#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob002_template_design.py
# Source description: https://www.csplib.org/Problems/prob002/
# Problem instances: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob002_template_design.json

"""
This problem arises from a colour printing firm which produces a variety of products from thin board,
including cartons for human and animal food and magazine inserts. Food products, for example, are often marketed as a
basic brand with several variations (typically flavours). Packaging for such variations usually has the same overall
design, in particular the same size and shape, but differs in a small proportion of the text displayed and/or in
colour. For instance, two variations of a cat food carton may differ only in that on one is printed ‘Chicken Flavour’
on a blue background whereas the other has ‘Rabbit Flavour’ printed on a green background. A typical order is for a
variety of quantities of several design variations. Because each variation is identical in dimension, we know in
advance exactly how many items can be printed on each mother sheet of board, whose dimensions are largely determined
by the dimensions of the printing machinery. Each mother sheet is printed from a template, consisting of a thin
aluminium sheet on which the design for several of the variations is etched. The problem is to decide, firstly,
how many distinct templates to produce, and secondly, which variations, and how many copies of each, to include on
each template. The given example is based on data from an order for cartons for different varieties of dry cat-food.

Print the number of printed sheets (production) for each template as a list, and the layout of the templates (layout) as a list of lists,
where each inner list represents the number of each variation on that template.
"""

# Data
n_slots = 9  # The amount of slots on a template
n_templates = 2  # The amount of templates
n_var = 7  # The amount of different variations
demand = [250, 255, 260, 500, 500, 800, 1100]  # The demand per variation
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
ub = max(demand)  # The upper bound for the production

# create model
model = Model()

# decision variables
production = intvar(1, ub, shape=n_templates, name="production")
layout = intvar(0, n_var, shape=(n_templates, n_var), name="layout")

# all slots are populated in a template
model += all(sum(layout[i]) == n_slots for i in range(n_templates))

# meet demand
for var in range(n_var):
    model += sum(production * layout[:, var]) >= demand[var]

# <SYMMETRY_BREAKING_CONSTRAINT_START>
# break symmetry
# equal demand
# for i in range(n_var - 1):
#     if demand[i] == demand[i + 1]:
#         model += layout[0, i] <= layout[0, i + 1]
#         for j in range(n_templates - 1):
#             model += (layout[j, i] == layout[j, i + 1]).implies(layout[j + 1, i] <= layout[j + 1, i + 1])

# distinguish templates
# for i in range(n_templates - 1):
#     model += production[i] <= production[i + 1]

# static symmetry
# for i in range(n_var - 1):
#     if demand[i] < demand[i + 1]:
#         model += sum(production * layout[:, i]) <= sum(production * layout[:, i + 1])
# <SYMMETRY_BREAKING_CONSTRAINT_END>

# minimize number of printed sheets
model.minimize(sum(production))

# Solve
model.solve()

# Print
solution = {"production": production.value().tolist(), "layout": layout.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
