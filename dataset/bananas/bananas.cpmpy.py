#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/bananas.py

"""
Five bananas cost three dollars, seven oranges cost five dollars, nine mangoes
cost seven dollars, and three apples cost nine dollars. I need to purchase
100 fruits in 100 dollars. Please keep in mind that all types
of fruits need to be purchased, but I do not like banana and apple, so
these should be of minimum quantity.

Print the quantities of each fruit (bananas, oranges, mangoes, apples).
"""

# Import libraries
from cpmpy import *
import json

x = intvar(1, 100, shape=4, name="x")
bananas, oranges, mangoes, apples = x

the_sum = intvar(1, 2000, name="the_sum")

model = Model([the_sum == bananas + apples,
               # This don't work since "/" does integer division
               # 3*bananas/5 + 5*oranges/7 + 7*mangoes/9 + 9*apples/3 == 100,
               # we multiply with 3*5*7*9=945 on both sides to weed out the divisions
               3 * bananas * 189 + 5 * oranges * 135 + 7 * mangoes * 105 + 9 * apples * 315 == 100 * 945,
               sum(x) == 100
               ])

model.minimize(the_sum)

# Solve the model
model.solve()

# Print the solution
solution = {
    "bananas": bananas.value(),
    "oranges": oranges.value(),
    "mangoes": mangoes.value(),
    "apples": apples.value()
}
print(json.dumps(solution))
# End of CPMPy script
