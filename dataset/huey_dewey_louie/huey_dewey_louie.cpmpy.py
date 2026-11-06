#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/huey_dewey_louie.py

# Import libraries
from cpmpy import *
import json

p = boolvar(shape=3)
huey, dewey, louie = p

model = Model([
    # Huey: Dewey and Louie has equal share in it; if one is quilty, so is the other.
    dewey == louie,

    # Dewey: If Huey is guilty, then so am I.
    huey.implies(dewey),

    # Louie: Dewey and I are not both guilty.
    ~(dewey & louie)
])

model.solve()

solution = {
    "huey": huey.value(),
    "dewey": dewey.value(),
    "louie": louie.value()
}
print(json.dumps(solution))
