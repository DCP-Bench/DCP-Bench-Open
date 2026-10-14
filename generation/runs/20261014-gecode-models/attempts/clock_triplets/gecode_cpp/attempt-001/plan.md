Rearrange the numbers on the face of a clock (1 to 12) -> x = IntVarArray(*this, 12, 1, 12) (one value per position, 1..12)
Each number from 1 to 12 appears once on the clock -> distinct(*this, x, IPL_DOM)
No triplet of adjacent numbers has a sum higher than 21 (the clock wraps: positions 11, 12, 1 are adjacent) -> linear(*this, {x[i], x[(i+1)%12], x[(i+2)%12]}, IRT_LQ, 21) for each i in 0..11
Branching -> branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN())
Objective -> none (satisfaction; the 21 bound is the given limit, not an optimum)
