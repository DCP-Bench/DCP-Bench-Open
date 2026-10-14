A Pythagorean triplet is a set of three natural numbers a < b < c -> a < b, b < c (ordering convention, needed for the uniqueness claim)
a^2 + b^2 = c^2 -> rel(a*a + b*b == c*c) on IntVars 1..1000 (sqr/mult, default propagation)
a + b + c = 1000 -> linear(*this, {1,1,1}, IRT_EQ, 1000) (bounds)
branching -> INT_VAR_SIZE_MIN, INT_VAL_MIN over {a, b, c}
objective -> none (satisfaction); outputs a, b, c as IntVar
