#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/zebra.py
# Description: https://en.wikipedia.org/wiki/Wolf,_goat_and_cabbage_problem
# Misc: Based on PyCSP3's Zebra.py by C. Lecoutre, https://github.com/xcsp3team/pycsp3/blob/master/problems/csp/single/Zebra.py

# Import libraries
from cpmpy import *
import json

n_houses = 5

# colors[i] is the house of the ith color
yellow, green, red, white, blue = colors = intvar(0,n_houses-1, shape=n_houses)

# nations[i] is the house of the inhabitant with the ith nationality
italy, spain, japan, england, norway = nations = intvar(0,n_houses-1, shape=n_houses)

# jobs[i] is the house of the inhabitant with the ith job
painter, sculptor, diplomat, pianist, doctor = jobs = intvar(0,n_houses-1, shape=n_houses)

# pets[i] is the house of the inhabitant with the ith pet
cat, zebra, bear, snails, horse = pets = intvar(0,n_houses-1, shape=n_houses)

# drinks[i] is the house of the inhabitant with the ith preferred drink
milk, water, tea, coffee, juice = drinks = intvar(0,n_houses-1, shape=n_houses)

model = Model(
    AllDifferent(colors),
    AllDifferent(nations),
    AllDifferent(jobs),
    AllDifferent(pets),
    AllDifferent(drinks),

    painter == horse,
    diplomat == coffee,
    white == milk,
    spain == painter,
    england == red,
    snails == sculptor,
    green + 1 == red,
    blue + 1 == norway,
    doctor == milk,
    japan == diplomat,
    norway == zebra,
    abs(green - white) == 1,
    #horse in {diplomat - 1, diplomat + 1},
    (horse == diplomat-1)|(horse == diplomat+1),
    #italy in {red, white, green}
    (italy == red)|(italy == white)|(italy == green),
)
model.solve()

# Print
solution = {
    "colors": colors.value().tolist(),
    "nations": nations.value().tolist(),
    "jobs": jobs.value().tolist(),
    "pets": pets.value().tolist(),
    "drinks": drinks.value().tolist(),
}
print(json.dumps(solution))
# End of CPMPy script
