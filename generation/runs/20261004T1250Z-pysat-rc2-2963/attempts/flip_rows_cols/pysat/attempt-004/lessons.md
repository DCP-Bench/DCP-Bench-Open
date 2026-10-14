When the optimum of a minimised integer sum is in the hundreds, unit-weight soft clauses
make RC2 raise the bound one core at a time: attempts 002 (per-entry weights) and 003
(per-row unit thresholds) timed out on the 27x9 example. A single order-encoded total with
threshold v weighted 1 + (v - 1) // (isqrt(N) + 1) has the same minimisers and lets
RC2Stratified's diversity rule (rc2.py next_level: break when the remaining selectors per
remaining level exceed half the number of levels) treat each block as a level, highest
first; the example then solved in 46 s. The link from the cells to the total used
EncType.adder, since PBEnc's default (BDD) over a thousand threshold literals is large.
