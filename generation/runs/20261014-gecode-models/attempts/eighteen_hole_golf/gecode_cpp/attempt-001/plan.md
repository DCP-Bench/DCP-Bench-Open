each of the 18 holes has a length of 3, 4, or 5 -> IntVarArray(*this, 18, 3, 5) (domain)
the total length of the course is 72 -> linear(*this, holes, IRT_EQ, 72) (default bounds propagation; sum of 18 variables)
branching -> branch(*this, holes, INT_VAR_SIZE_MIN(), INT_VAL_MIN())
objective -> none (satisfaction)
