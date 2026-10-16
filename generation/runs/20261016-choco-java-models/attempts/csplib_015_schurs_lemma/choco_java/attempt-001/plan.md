put n balls labelled 1..n into 3 boxes -> M[i][j] BoolVar, ball i in box j (m.boolVarMatrix n x c), instance fields n and c
a ball must be in exactly one box, M_i1 + M_i2 + M_i3 = 1 -> m.sum(row, "=", 1)
for any triple (x, y, z) with x + y = z, not all in the same box -> for each triple and box j: M_xj + M_yj + M_zj <= 2 (m.sum "<=" 2)
triples enumerated over 1..n with x <= y and z = x + y <= n
print the assignment of balls to boxes as integers 1..3 -> balls[i] = sum_j (j+1) * M[i][j] (m.scalar with "=" and an IntVar)
Objective: none (satisfaction)
