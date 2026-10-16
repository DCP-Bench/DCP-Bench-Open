The product of their ages is 36 -> a[0]*a[1]*a[2] == 36 via two aux products: rel(*this, ab == a[0]*a[1]); rel(*this, ab*a[2] == 36) (arithmetic, bounds)
Ages are positive whole numbers -> IntVarArray a(*this, 3, 1, 36) (a product of three ages >= 1 that is 36 bounds each age by 36)
Print from the oldest -> a[0] >= a[1] >= a[2] via rel(*this, a[i] >= a[i+1]) (ordering convention, not a clue)
The sum of their ages equals the number of windows (unknown, free) -> sa = expr(*this, sum(a)); no windows variable is an output
Mathematician needs more info after the sum: another triple with product 36 and the same sum exists -> witness triple b (sorted, b[0] >= b[1] >= b[2], product 36) with rel(*this, sum(b) == sa) -> arithmetic; the witness is branched on like a
The witness is a different triple, not a permutation: at least one position differs -> differs[i] = expr(*this, a[i] != b[i]); linear(*this, differs, IRT_GQ, 1) (linear over BoolVars)
The oldest son has blue eyes and the mathematician got it: the oldest age is unique -> rel(*this, a[0] > a[1]) (strict)
Branching -> branch(*this, a, INT_VAR_SIZE_MIN(), INT_VAL_MIN()) then branch(*this, b, INT_VAR_SIZE_MIN(), INT_VAL_MIN())
Objective -> none (satisfaction); outputs A1, A2, A3 are a[0], a[1], a[2]
