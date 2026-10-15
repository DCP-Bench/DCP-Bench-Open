"""Perfect square placement (squared square).

Pack n squares, with the given integer sides, into a base x base square so that
no two squares overlap and all borders are parallel to the big square's border.
The squares cover the packing square exactly. Output the lower-left corner of
each square, 0-based, as x_coords and y_coords.

Encoding: each coordinate is a unary (order) integer. Bool xge[i][k] means
x_i >= k + 1, and the chain xge[k+1] -> xge[k] makes it a proper order.
"""

from paramita.modelling import Bool, If, Or


def build(instance):
    base = instance["base"]
    sides = instance["sides"]
    n = len(sides)

    # Coordinates of square i range over 0 .. base - sides[i].
    def unary_coord(prefix, i):
        top = base - sides[i]
        bits = [Bool(f"{prefix}_ge_{i}_{k}") for k in range(1, top + 1)]
        chain = [If(bits[k + 1], bits[k]) for k in range(len(bits) - 1)]
        return bits, chain

    xbits, xcons = [], []
    ybits, ycons = [], []
    for i in range(n):
        b, c = unary_coord("x", i)
        xbits.append(b)
        xcons += c
        b, c = unary_coord("y", i)
        ybits.append(b)
        ycons += c

    x = [sum(xbits[i]) for i in range(n)]
    y = [sum(ybits[i]) for i in range(n)]

    cons = xcons + ycons

    # A square stays inside the base square.
    # (The unary domain already limits x_i and y_i to base - sides[i].)

    # No two squares overlap: each pair is separated horizontally or vertically.
    for i in range(n):
        for j in range(i + 1, n):
            left = Bool(f"left_{i}_{j}")       # square i lies left of square j
            right = Bool(f"left_{j}_{i}")      # square j lies left of square i
            below = Bool(f"below_{i}_{j}")     # square i lies below square j
            above = Bool(f"below_{j}_{i}")     # square j lies below square i
            cons.append(Or([left, right, below, above]))
            # x_i + sides[i] <= x_j when i is left of j
            cons.append(If(left, x[i] + sides[i] <= x[j]))
            cons.append(If(right, x[j] + sides[j] <= x[i]))
            # y_i + sides[i] <= y_j when i is below j
            cons.append(If(below, y[i] + sides[i] <= y[j]))
            cons.append(If(above, y[j] + sides[j] <= y[i]))

    return cons, {"x_coords": x, "y_coords": y}
