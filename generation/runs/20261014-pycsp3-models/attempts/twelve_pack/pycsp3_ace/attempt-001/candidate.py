from pycsp3 import *

# Twelve-pack problem: find the combination of packs of the given sizes that meets or exceeds the
# target number of items, with the fewest items overall (the closest combination from above).
packs = data.packs
target = data.target
n = len(packs)

# counts[k] is the number of packs of size packs[k] used
counts = VarArray(size=n, dom=range(0, target + 1))

satisfy(
    # the packs used hold at least the target number of items
    Sum(packs[k] * counts[k] for k in range(n)) >= target,
)

# the total number of items is as small as possible
minimize(Sum(packs[k] * counts[k] for k in range(n)))
