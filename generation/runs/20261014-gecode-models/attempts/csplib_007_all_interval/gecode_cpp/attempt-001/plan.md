each of the twelve pitch-classes occurs exactly once in the series -> distinct(*this, x, IPL_DOM) [x is a permutation of 0..n-1]
the intervals between neighbouring notes cover the full set of intervals from 1 to n-1 -> distinct(*this, diffs, IPL_DOM) [diffs has n-1 vars, domain 1..n-1, all different, so a permutation]
diffs[i] is the interval between neighbouring notes x[i] and x[i+1] -> abs(*this, expr(*this, x[i+1] - x[i]), diffs[i], IPL_DOM) [one abs per neighbouring pair]
symmetry: reversing a series gives another series -> rel(*this, x[0] < x[n-1]) [symmetry break, does not remove all solutions]
branching -> branch(*this, x, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN()) with restarts(100); then branch(*this, diffs, INT_VAR_SIZE_MIN(), INT_VAL_MIN())
objective -> none (satisfaction)
