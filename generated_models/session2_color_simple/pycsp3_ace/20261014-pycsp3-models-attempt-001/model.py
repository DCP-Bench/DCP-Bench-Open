from pycsp3 import *

# the six countries: Belgium, Denmark, France, Germany, Netherlands, Luxembourg (numbered 1 to 6 in the graph)
colors = VarArray(size=6, dom=range(1, 7))

satisfy(
    # two neighbouring countries cannot have the same colour
    [colors[i - 1] != colors[j - 1] for i, j in data.graph],
)

# the number of colours used is as small as possible: the largest colour number is minimised
minimize(Maximum(colors))
