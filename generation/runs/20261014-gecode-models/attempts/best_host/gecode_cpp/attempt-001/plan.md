Six guests seated in a round, each guest next to two others (seat k next to seat k+1 mod 6) -> circular adjacency over x[0..5]
Each guest sits in one seat, seats hold distinct guests -> distinct(*this, x, IPL_DOM)
Each guest sits next to only the two guests they get along with (Andrew: Dave, Frank; ...) -> pairs of adjacent seats not in the get-along list are conflicts; table of conflicting ordered pairs via TupleSet, reified per adjacent seat pair: extensional(*this, {x[k], x[k+1]}, conflictTuples, true, Reify(c_k, RM_EQV), IPL_DOM) (c_k = 1 iff the neighbours do not get along)
Number of conflicts is the number of conflicting adjacent pairs -> conflicts = expr(*this, sum(c_k))
Minimise conflicts -> minimize(conflicts)
Branching: seat assignment x, INT_VAR_SIZE_MIN, INT_VAL_MIN (the c_k follow from x)
Output: x (seat order, guest ids 0..5)
