#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/allergy.py

"""
Four friends (two women named Debra and Janet, and two men named Hugh and Rick) found
that each of them is allergic to something different:
eggs, mold, nuts and ragweed.
We would like to match each one's surname (Baxter, Lemon, Malone and Fleet) with his or her allergy.
We know that:
 - Rick is not allergic to mold
 - Baxter is allergic to eggs
 - Hugh is neither surnamed Lemon nor Fleet
 - Debra is allergic to ragweed
 - Janet (who isn't Lemon) is neither allergic to eggs nor to mold

Print the values of each food (eggs, mold, nuts, ragweed) and surname (baxter, lemon, malone, fleet) for each friend,
where Debra = 0, Janet = 1, Hugh = 2, Rick = 3.
"""

# Import libraries
from cpmpy import *
import json

n = 4
friends = Debra, Janet, Hugh, Rick = list(range(n))
friends_s = ["Debra", "Janet", "Hugh", "Rick"]

# foods[i] is the friend allergic to the ith food
eggs, mold, nuts, ragweed = foods = intvar(0, n - 1, shape=n, name="foods")
foods_s = ["eggs", "mold", "nuts", "ragweed"]

# surnames[i] is the friend with the ith surname
baxter, lemon, malone, fleet = surnames = intvar(0, n - 1, shape=n, name="surnames")
surnames_s = ["baxter", "lemon", "malone", "fleet"]

model = Model([AllDifferent(foods),
               AllDifferent(surnames),

               mold != Rick,
               eggs == baxter,
               lemon != Hugh,
               fleet != Hugh,
               ragweed == Debra,
               lemon != Janet,
               eggs != Janet,
               mold != Janet])

# Solve
model.solve()

# Print the solution
solution = {"eggs": eggs.value(), "mold": mold.value(), "nuts": nuts.value(), "ragweed": ragweed.value(),
            "baxter": baxter.value(), "lemon": lemon.value(), "malone": malone.value(), "fleet": fleet.value()}
print(json.dumps(solution))
# End of CPMPy script
