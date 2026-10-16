"cyclic sequence in which every possible length-n string on A occurs exactly once" -> x[i] over alphabet 0..base-1 in a cycle of length base^n; code_i = sum_t x[(i+t) mod L] * base^t is the window value starting at i (scalar, cyclic indices)
"every possible length-n string occurs exactly once" -> allDifferent over the L window codes (L = base^n codes, so each value is used exactly once) with "AC"
"print the sequence of a given order on a given alphabet" -> de_bruijn = x, length base^n
Objective: none (satisfaction).
