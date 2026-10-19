"""Graph colouring with the fewest colours. The number of distinct colours is the
objective, so the optimum is the chromatic number. The wheel below (a five-cycle with a
hub joined to every rim node) needs 4 colours."""
from pycsp3 import *

n = 6
hub = 5
edges = [(i, (i + 1) % hub) for i in range(hub)] + [(i, hub) for i in range(hub)]
colour = VarArray(size=n, dom=range(n), id="colour")

satisfy(
    # the two ends of every edge get different colours
    [colour[u] != colour[v] for u, v in edges],
)
# fewer distinct colours is better
minimize(NValues(colour))

status = solve()
if status is OPTIMUM:
    print("Colours:", bound())
    print("Colour of each node:", values(colour))
else:
    print("Status:", status)
