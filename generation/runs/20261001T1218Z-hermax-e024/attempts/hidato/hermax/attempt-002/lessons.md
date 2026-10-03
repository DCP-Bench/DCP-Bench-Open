Large permutation constraints in hermax (measured, cause not inspected)

hidato attempt-001 posted `bool_matrix.row(c).exactly_one()` and `.col(c).exactly_one()` over 144 x 144
entries. Evaluation: 8x8 instance 58.9 s, 12x12 example killed at 190 s with no runner status.
attempt-002 replaced them by a ladder exactly-one written with plain Boolean clauses and removed
(cell, number) pairs ruled out by the given numbers: all five instances 1.1 to 1.7 s.
knights_tour attempt-001 (same row/col exactly_one over n*n x n*n): 8x8 62 s, 10x10 killed at 190 s;
attempt-002 (ladder exactly-one plus successor edges): 10x10 6.3 s.
Time grew roughly like N^3.8 in the number of squares between 6x6 and 8x8 for attempt-001. Two changes
were made together in each case, so the effect of the ladder alone is not isolated.
