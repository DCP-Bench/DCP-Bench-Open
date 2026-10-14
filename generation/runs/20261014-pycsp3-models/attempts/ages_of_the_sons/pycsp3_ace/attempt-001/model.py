from pycsp3 import *

# The product of the three ages is 36. The sons' ages are listed oldest first,
# so each candidate is a triple a >= b >= c of positive whole numbers.
# The candidate triples are enumerated from that product.
candidates = [(a, b, c) for a in range(1, 37) for b in range(1, a + 1) for c in range(1, b + 1) if a * b * c == 36]

# the ages of the three sons, oldest first
A1 = Var(dom=range(1, 37))
A2 = Var(dom=range(1, 37))
A3 = Var(dom=range(1, 37))

# the product of their ages is 36
satisfy(Table(scope=[A1, A2, A3], supports=candidates))

# the mathematician needs more information: the sum of the ages equals the number of
# windows, and another set of ages with product 36 has the same sum
B1 = Var(dom=range(1, 37))
B2 = Var(dom=range(1, 37))
B3 = Var(dom=range(1, 37))
satisfy(
    Table(scope=[B1, B2, B3], supports=candidates),
    Sum(B1, B2, B3) == Sum(A1, A2, A3),
    Or(B1 != A1, B2 != A2, B3 != A3),
)

# the oldest son has blue eyes, so the oldest son is a single son
satisfy(A1 > A2)

# the mathematician got it: among the candidates with the same sum, only one has a single oldest son
for (c1, c2, c3) in candidates:
    if c1 > c2:
        satisfy(
            imply(Sum(A1, A2, A3) == c1 + c2 + c3, A1 == c1),
            imply(Sum(A1, A2, A3) == c1 + c2 + c3, A2 == c2),
            imply(Sum(A1, A2, A3) == c1 + c2 + c3, A3 == c3),
        )
