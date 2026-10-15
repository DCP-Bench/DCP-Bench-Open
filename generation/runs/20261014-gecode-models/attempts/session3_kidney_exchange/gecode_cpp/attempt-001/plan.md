at the hospital n people are on a waiting list -> succ = IntVarArray(*this, n, 0, n-1), one variable per person (0-based, data is 1-based)
compatible[i] is the set of people to which i can donate -> dom(*this, succ[i], IntSet({i} + compatible[i])); i itself stays in the domain as "takes part in no transplant"
anyone who gives a kidney must receive one, and no person receives more than one kidney -> distinct(*this, succ, IPL_DOM) (succ is a permutation: disjoint cycles, self loops are idle people)
transplants[i][j] is 1 if person i donates to person j -> rel(*this, succ[i], IRT_EQ, j, b_ij) (full reification), transplants[i][i] = 0 constant
maximize the number of people who receive a kidney -> receivers = expr(*this, sum(all b_ij)), maximize(receivers)
branching -> branch(succ, INT_VAR_SIZE_MIN(), INT_VAL_MIN()); transplants bools are fixed once succ is
