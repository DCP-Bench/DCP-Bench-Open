Find four different numbers between 1 and 100 such that the sum of the squares of the two first numbers equals the sum of the squares of the other two (a^2 + b^2 = c^2 + d^2).
Each of a, b, c, d lies in 1..100 -> IntVar a, b, c, d in 1..100 (domains from the problem statement).
a, b, c, d are different (a != b != c != d, read as all pairwise different) -> distinct(*this, {a,b,c,d}, IPL_DOM)
the squares a^2, b^2, c^2, d^2 -> sqr(*this, x, s, IPL_DEF) for each, with s in 1..10000 (arithmetic row, default propagation)
a^2 + b^2 = c^2 + d^2 -> rel(*this, sa + sb == sc + sd) (linear over the square variables, default bounds)
branching -> branch(*this, {a,b,c,d}, INT_VAR_SIZE_MIN(), INT_VAL_MIN()); the squares are functions of these, so no other decision variables.
objective -> none (satisfaction); outputs a, b, c, d.
