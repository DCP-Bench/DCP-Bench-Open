from pycsp3 import *

# Rectangle packing: place the items (widths and heights given) inside a larger rectangle of size
# total_x by total_y without overlap, all inside the boundary, and minimise the area of the rectangle.
# Positions start at 0; items are not rotated.
widths = data.widths
heights = data.heights
n = len(widths)
sum_w = sum(widths)
sum_h = sum(heights)

# pos_x[i], pos_y[i] are the lower left corner of item i
pos_x = VarArray(size=n, dom=range(0, sum_w))
pos_y = VarArray(size=n, dom=range(0, sum_h))

# dimensions of the enclosing rectangle
total_x = Var(dom=range(max(widths), sum_w + 1))
total_y = Var(dom=range(max(heights), sum_h + 1))

satisfy(
    # every item lies within the enclosing rectangle, to the right and at the top
    [pos_x[i] + widths[i] <= total_x for i in range(n)],
    [pos_y[i] + heights[i] <= total_y for i in range(n)],
    # no two items overlap: one is left of, right of, below or above the other
    [Or(pos_x[i] + widths[i] <= pos_x[j],
        pos_x[j] + widths[j] <= pos_x[i],
        pos_y[i] + heights[i] <= pos_y[j],
        pos_y[j] + heights[j] <= pos_y[i])
     for i in range(n) for j in range(i + 1, n)],
)

# the area of the enclosing rectangle is as small as possible
minimize(total_x * total_y)
