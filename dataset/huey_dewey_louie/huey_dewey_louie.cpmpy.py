#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/huey_dewey_louie.py

"""
Huey, Dewey and Louie are being questioned by their uncle. These are the
statements the make:
  Huey: Dewey and Louie has equal share in it; if one is quilty, so is the other.
  Dewey: If Huey is guilty, then so am I.
  Louie: Dewey and I are not both guilty.

Their uncle, knowing that they are cub scouts, realises that they cannot tell a lie.
Has he got sufficient information to decide who (if any) are quilty?

Print whether Huey, Dewey, and Louie (huey, dewey, louie) are guilty or not.
"""

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
