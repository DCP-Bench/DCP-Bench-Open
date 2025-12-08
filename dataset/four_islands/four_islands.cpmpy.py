#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/four_islands.py
# Source description: http://brownbuffalo.sourceforge.net/FourIslandsClues.html

"""
A tiny nation in the South Pacific contains four islands connected by bridges
as shown (see below). Each of the four islands (Pwana, Quero, Rayou, and Skern)
boasts a different primary export (alabaster, bananas, coconuts, and durian
fruit) and a different tourist attraction (hotel, ice skating rink, jai alai
stadium, and koala preserve). Can you find the name, export, and tourist
attraction of each island on the map?

A, B, C, D are the islands, this is the map showing the bridges and the orientation of the islands:

(A) -- (B)
 |      |
 |      |
(C) -- (D)

This means that A is north of B, C is west of D, etc.

1. The island noted for its koala preserve is due south of Pwana.
2. The island with the largest alabaster quarry is due west of Quero.
3. The island with the resort hotel is due east of the one that exports
   durian fruit.
4. Skern and the island with the jai alai stadium are connected by a
   north-south bridge.
5. Rayou and the island that exports bananas are connected by an east-west
   bridge.
6. The islands noted for the South Pacific's largest ice skating rink and
   for the jai alai stadium are not connected by a bridge.

Determine: Island name -- Export -- Tourist Attraction

Print a number for each island (island), export (export), and attraction (attraction) as lists of integers from 0 to
3, where the same number represents a mapping between the three categories. Use the same order as mentioned above.
Also, 0 should represent A in the given map above, 1 should represent B, and so on.
"""

# Import libraries
from cpmpy import *
import numpy as np
import json

model = Model()

n = 4

[A, B, C, D] = range(n)

island = intvar(0, n - 1, shape=n, name="island")
Pwana, Quero, Rayou, Skern = island

export = intvar(0, n - 1, shape=n, name="export")
alabaster, bananas, coconuts, durian_fruit = export

attraction = intvar(0, n - 1, shape=n, name="attraction")
resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = attraction

model += [AllDifferent(island),
          AllDifferent(export),
          AllDifferent(attraction)]

# 1. The island noted for its koala preserve is due south of Pwana.
model += [
    ((Pwana == A) & (koala_preserve == C))
    |
    ((Pwana == B) & (koala_preserve == D))
]

# 2. The island with the largest alabaster quarry is due west of Quero.
model += [
    ((alabaster == A) & (Quero == B))
    |
    ((alabaster == C) & (Quero == D))
]

# 3. The island with the resort hotel is due east of the one that exports
#    durian fruit.
model += [
    ((durian_fruit == A) & (resort_hotel == B))
    |
    ((durian_fruit == C) & (resort_hotel == D))
]

# 4. Skern and the island with the jai alai stadium are connected by a
#    north-south bridge.
model += [
    ((Skern == A) & (jai_alai_stadium == C))
    |
    ((Skern == C) & (jai_alai_stadium == A))
    |
    ((Skern == B) & (jai_alai_stadium == D))
    |
    ((Skern == D) & (jai_alai_stadium == B))
]

# 5. Rayou and the island that exports bananas are connected by an
#    east-west bridge.
model += [
    ((Rayou == A) & (bananas == B))
    |
    ((Rayou == B) & (bananas == A))
    |
    ((Rayou == C) & (bananas == D))
    |
    ((Rayou == D) & (bananas == C))
]

# 6. The islands noted for the South Pacific's largest ice skating rink
#    and for the jai alai stadium are not connected by a bridge.
model += [
    ((ice_skating_rink == A) & (jai_alai_stadium == D))
    |
    ((ice_skating_rink == D) & (jai_alai_stadium == A))
    |
    ((ice_skating_rink == B) & (jai_alai_stadium == C))
    |
    ((ice_skating_rink == C) & (jai_alai_stadium == B))
]

model.solve()

solution = {
    "island": island.value().tolist(),
    "export": export.value().tolist(),
    "attraction": attraction.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script
