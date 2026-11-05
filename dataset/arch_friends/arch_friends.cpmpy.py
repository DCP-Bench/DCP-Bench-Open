#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/arch_friends.py

# Import libraries
from cpmpy import *
import numpy as np
import json


n = 4
model = Model()

shoes = intvar(1, n, shape=n, name="shoes")
ecruespadrilles, fuchsiaflats, purplepumps, suedesandals = shoes

store = intvar(1, n, shape=n, name="store")
footfarm, heelsinahandcart, theshoepalace, tootsies = store

model += [AllDifferent(shoes),
          AllDifferent(store),

          # 1. Harriet bought fuchsia flats at Heels in a Handcart.
          fuchsiaflats == heelsinahandcart,

          # 2. The store she visited just after buying her purple pumps was not
          #    Tootsies.
          purplepumps + 1 != tootsies,

          # 3. The Foot Farm was Harriet's second stop.
          footfarm == 2,

          # 4. Two stops after leaving The Shoe Place, Harriet bought her suede
          # sandals.
          theshoepalace + 2 == suedesandals
          ]

model.solve()

# Print
solution = {"ecruespadrilles": ecruespadrilles.value(),
            "fuchsiaflats": fuchsiaflats.value(),
            "purplepumps": purplepumps.value(),
            "suedesandals": suedesandals.value(),
            "footfarm": footfarm.value(),
            "heelsinahandcart": heelsinahandcart.value(),
            "theshoepalace": theshoepalace.value(),
            "tootsies": tootsies.value()
            }
print(json.dumps(solution))
# End of CPMPy script
