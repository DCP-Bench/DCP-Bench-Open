#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/allergy.py

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
