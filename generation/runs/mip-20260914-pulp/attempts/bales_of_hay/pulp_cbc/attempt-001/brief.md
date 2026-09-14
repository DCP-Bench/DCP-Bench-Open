# bales_of_hay
Instance: `n`, `weights`. Output: `bales` — n integers in 0..50. Every listed
weight is the sum of some pair of distinct bales.
The reference states that with a fresh pair of index variables per weight; here
each weight picks one pair through binaries, and the chosen pair's sum is
forced by a big-M pair of inequalities whose M is the largest sum two bales can
have. The commented-out ordering constraint is symmetry breaking and is not
carried over.
