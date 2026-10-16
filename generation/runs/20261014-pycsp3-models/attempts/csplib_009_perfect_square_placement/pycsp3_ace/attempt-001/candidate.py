from pycsp3 import *

# pack the squares with the given sides into a square of the given base, without overlaps
base = data.base
sides = data.sides
n = len(sides)
# x_coords[i] is the column of the left border of square i, counted from 0
x_coords = VarArray(size=n, dom=range(base))
# y_coords[i] is the row of the bottom border of square i, counted from 0
y_coords = VarArray(size=n, dom=range(base))
satisfy(
    # every square lies inside the big square, horizontally
    [x_coords[i] <= base - sides[i] for i in range(n)],
    # every square lies inside the big square, vertically
    [y_coords[i] <= base - sides[i] for i in range(n)],
    # no two squares overlap: one is left of, right of, below or above the other
    [Or(x_coords[i] + sides[i] <= x_coords[j],
        x_coords[j] + sides[j] <= x_coords[i],
        y_coords[i] + sides[i] <= y_coords[j],
        y_coords[j] + sides[j] <= y_coords[i])
     for i in range(n) for j in range(i + 1, n)],
)
