Enter the digits 1 through 8 in the circles and squares -> IntVarArray p[8] over 1..8, distinct(*this, p, IPL_DOM) (each digit once)
the number in each square is equal to the sum of the adjoining circles (top middle = top-left + top-right) -> rel(*this, p[0] + p[2] == p[1])
(left middle = top-left + bottom-left) -> rel(*this, p[0] + p[5] == p[3])
(right middle = top-right + bottom-right) -> rel(*this, p[2] + p[7] == p[4])
(bottom middle = bottom-left + bottom-right) -> rel(*this, p[5] + p[7] == p[6])
redundant: the four circles sum to 12 (total 36 = circles + squares = 3 x circles) -> linear(*this, circles, IRT_EQ, 12) with IPL_DOM distinct kept
branching: all 8 positions, INT_VAR_SIZE_MIN, INT_VAL_MIN (8 variables, no need for more)
objective: none (satisfaction); output positions as declared
