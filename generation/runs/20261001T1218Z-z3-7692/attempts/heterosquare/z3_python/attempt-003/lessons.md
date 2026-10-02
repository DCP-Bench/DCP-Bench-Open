# Lesson: all-different over many integer cells in z3_python

Order 6 and 7 timed out with `z3.Distinct` over the n^2 integer cells (attempt-001: no second
solution within 180 s). A bit-vector version (attempt-002) solved order 6 in 11 s but found no
solution for order 7 in 180 s. Stating "every value 1..n^2 occurs exactly once" as
`z3.PbEq([(x[i][j] == v, 1) for all cells], 1)` for each value v, keeping the cells as Ints,
solved all five instances in at most 7.2 s (attempt-003 evaluation.json). `Distinct` was kept
for the 2n + 2 sums, with sum bounds tightened to the minimum and maximum of n distinct values.
