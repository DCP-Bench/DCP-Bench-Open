The first mark is at 0 -> rel(*this, marks[0] == 0)
Marks a_1 < a_2 < ... < a_m, the integers of the ruler -> rel(*this, marks[i], IRT_LE, marks[i+1]) (strict)
The m(m-1)/2 differences a_j - a_i (i < j) are all different -> expr(*this, marks[j] - marks[i]) per pair, then distinct(*this, differences, IPL_DOM) [pairwise distinct globals rather than decomposition; IPL_DOM because the domains are tight]
The length is the position of the last mark -> length = marks[m-1] (shares the variable)
Branching: build the ruler from the first mark on, smallest position first -> branch(*this, marks, INT_VAR_NONE(), INT_VAL_MIN())
Objective: minimise the length -> minimize(length)
