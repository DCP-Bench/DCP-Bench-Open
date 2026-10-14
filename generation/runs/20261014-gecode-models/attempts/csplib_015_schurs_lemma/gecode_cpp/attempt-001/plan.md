put n balls labelled 1..n into 3 boxes -> IntVarArray balls(*this, n, 1, c), one box per ball, c = instance field c
each ball is in exactly one box -> the domain 1..c of each variable
boxes are interchangeable (symmetry) -> precede(*this, balls, IntArgs({1..c})) (box v+1 first used after box v)
for any triple (x, y, z) with x + y = z, x <= y (x = y allowed), not all three in the same box -> rel(*this, (balls[x] != balls[y]) || (balls[y] != balls[z])) (logic row of the map)
branching -> branch(*this, balls, INT_VAR_SIZE_MIN(), INT_VAL_MIN())
objective -> none (satisfaction)
