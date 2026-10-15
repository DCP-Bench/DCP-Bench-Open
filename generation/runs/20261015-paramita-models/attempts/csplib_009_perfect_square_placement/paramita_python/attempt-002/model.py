"""Perfect square placement (squared square).

Pack n squares, with the given integer sides, into a base x base square so that
no two squares overlap and all borders are parallel to the big square's border.
The squares cover the packing square exactly. Output the lower-left corner of
each square, 0-based, as x_coords and y_coords.

Encoding: each coordinate is a unary (order) integer. Bool xge[i][k] means
coordinate i is at least k + 1; the chain xge[k+1] -> xge[k] keeps it an order.
The separation of two squares is written as clauses over these order bits, so
no pseudo-Boolean constraint is needed.
"""

from paramita.modelling import Bool, If, Or


def build(instance):
    base = instance["base"]
    sides = instance["sides"]
    n = len(sides)

    def unary_coord(prefix, i):
        top = base - sides[i]                       # coordinate in 0..top
        bits = [Bool(f"{prefix}_ge_{i}_{k}") for k in range(1, top + 1)]
        chain = [If(bits[k + 1], bits[k]) for k in range(len(bits) - 1)]
        return bits, chain

    xbits, ybits, cons = [], [], []
    for i in range(n):
        b, c = unary_coord("x", i)
        xbits.append(b)
        cons += c
        b, c = unary_coord("y", i)
        ybits.append(b)
        cons += c

    x = [sum(xbits[i]) for i in range(n)]
    y = [sum(ybits[i]) for i in range(n)]

    def add_before(cond, bits_a, s_a, bits_b, top_b):
        # cond -> (a + s_a <= b), with a and b coordinates in unary bits.
        # For each k: (a >= k) implies (b >= k + s_a).
        # The literal "a >= k" is bits_a[k - 1], and is true for k = 0.
        # The literal "b >= m" is bits_b[m - 1]; it is true for m <= 0 and
        # false for m > top_b, so that term drops out of the clause.
        for k in range(0, len(bits_a) + 1):
            m = k + s_a
            if m <= 0:
                continue
            clause = [~cond]
            if k >= 1:
                clause.append(~bits_a[k - 1])
            if m <= top_b:
                clause.append(bits_b[m - 1])
            if len(clause) == 1:
                cons.append(clause[0])
            else:
                cons.append(Or(clause))

    # No two squares overlap: each pair is separated horizontally or vertically.
    for i in range(n):
        for j in range(i + 1, n):
            left = Bool(f"left_{i}_{j}")       # square i lies left of square j
            right = Bool(f"left_{j}_{i}")      # square j lies left of square i
            below = Bool(f"below_{i}_{j}")     # square i lies below square j
            above = Bool(f"below_{j}_{i}")     # square j lies below square i
            cons.append(Or([left, right, below, above]))
            # x_i + sides[i] <= x_j when i is left of j
            add_before(left, xbits[i], sides[i], xbits[j], base - sides[j])
            # x_j + sides[j] <= x_i when j is left of i
            add_before(right, xbits[j], sides[j], xbits[i], base - sides[i])
            # y_i + sides[i] <= y_j when i is below j
            add_before(below, ybits[i], sides[i], ybits[j], base - sides[j])
            # y_j + sides[j] <= y_i when j is below i
            add_before(above, ybits[j], sides[j], ybits[i], base - sides[i])

    return cons, {"x_coords": x, "y_coords": y}
