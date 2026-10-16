from pycsp3 import *

# Circling the squares: ten numbers sit in a circle in the order A B C D E F G H I K. The sum of the
# squares of any two adjacent numbers equals the sum of the squares of the two numbers diametrically
# opposite to them. Whole numbers of at most two figures, all different. A=16, B=2, F=8, G=14.

# lowercase names; the output names are aliased below
a = Var(dom=range(1, 100))
b = Var(dom=range(1, 100))
c = Var(dom=range(1, 100))
d = Var(dom=range(1, 100))
e = Var(dom=range(1, 100))
f = Var(dom=range(1, 100))
g = Var(dom=range(1, 100))
h = Var(dom=range(1, 100))
i = Var(dom=range(1, 100))
k = Var(dom=range(1, 100))
A, B, C, D, E, F, G, H, I, K = a, b, c, d, e, f, g, h, i, k

# the ten numbers in circle order, so the diametrically opposite position of k is k + 5 (mod 10)
ring = [a, b, c, d, e, f, g, h, i, k]

# sq[p] is the square of the number at position p of the circle
sq = VarArray(size=10, dom=range(1, 100 * 100))

satisfy(
    # the ten numbers are all different
    AllDifferent(ring),
    # each number is linked to its square
    [Table(scope=[ring[p], sq[p]], supports=[(v, v * v) for v in range(1, 100)]) for p in range(10)],
    # the numbers placed as examples: A is 16, B is 2, F is 8 and G is 14
    A == 16,
    B == 2,
    F == 8,
    G == 14,
    # two adjacent numbers and the two numbers opposite them have equal sums of squares
    # (A and B to F and G, B and C to G and H, and so on around the circle)
    [sq[p] + sq[(p + 1) % 10] == sq[(p + 5) % 10] + sq[(p + 6) % 10] for p in range(10)],
)
