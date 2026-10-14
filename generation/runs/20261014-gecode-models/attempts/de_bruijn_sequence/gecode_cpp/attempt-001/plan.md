Problem: de Bruijn sequence B(k, n): a cyclic sequence over k symbols, length k^n, in which every length-n string occurs exactly once as a (cyclic) substring.

Requirement: the sequence has length k^n over alphabet 0..k-1 (k = base, n = order, from the instance) -> IntVarArray x of length base^n, domains 0..base-1.
Requirement: a cyclic sequence, so windows wrap around -> window i reads x[(i+j) mod L] for j = 0..n-1.
Requirement: every length-n string occurs exactly once -> window value w_i = sum_j x[(i+j) mod L] * base^(n-1-j) (one linear per window, w_i in 0..L-1) -> linear(*this, coeffs, vars, IRT_EQ, 0) with w_i carrying -1.
Requirement: the windows are pairwise different, so all strings occur -> distinct(*this, w, IPL_DOM). (L windows and L strings, so distinct means each string occurs exactly once.)
Branching: decisions are the symbols x (INT_VAR_NONE, INT_VAL_MIN); then the window values w, which the linear posts fix once x is fixed.
Objective: none (satisfaction). Output: de_bruijn = x.
