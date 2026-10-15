# Plan: Joe's account number (just_forgotten)

Requirement lines in the description's words, each -> Gecode post.

- the account number has all the digits from 0 to n-1 in some order -> distinct(*this, x, IPL_DOM) over x[0..n-1] with domains 0..n-1 (permutation; the count n comes from the sets)
- in each set just a specific number of the digits are in their correct position -> for each set s and position i, b[s][i] = expr(x[i] == sets[s][i]) (BoolVar, one per position); linear(*this, b[s], IRT_EQ, num_correct_digits) (reified equalities, the map has no row for "count of positions matching a fixed array")
- the account number is determined by the sets -> no extra constraint; uniqueness comes from the sets
- branching -> branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN()) (permutation search, first fail)
- objective -> satisfaction, no objective
- output "x" -> output("x", x)
