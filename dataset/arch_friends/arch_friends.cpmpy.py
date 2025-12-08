#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/arch_friends.py

"""
Harriet, upon returning from the mall, is happily describing her four
shoe purchases to her friend Aurora. Aurora just loves the four
different kinds of shoes that Harriet bought
  (ecru espadrilles, fuchsia flats, purple pumps, and suede sandals),
but Harriet can't recall at which different store
  (Foot Farm, Heels in a Handcart, The Shoe Palace, or Tootsies)
she got each pair. Can you help these two figure out the order in
which Harriet bought each pair of shoes, and where she bought each?

1. Harriet bought fuchsia flats at Heels in a Handcart.
2. The store she visited just after buying her purple pumps was not
  Tootsies.
3. The Foot Farm was Harriet's second stop.
4. Two stops after leaving The Shoe Place, Harriet bought her suede
  sandals.

Print the values of each shoe (ecruespadrilles, fuchsiaflats, purplepumps, suedesandals) and store (footfarm,
heelsinahandcart, theshoepalace, tootsies), such that the same value denotes the same shoe or store; values are integers from 1 to 4.
"""

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
