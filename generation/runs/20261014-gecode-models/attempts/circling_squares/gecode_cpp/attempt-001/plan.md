# Plan: circling_squares (attempt-001)

Ring order of the ten squares: v[0..9] = A B C D E F G H I K. Opposite of position i is i+5 mod 10.

- ten different numbers in the ten squares -> distinct(*this, v, IPL_DOM)
- fractions not allowed, integers of at most two figures -> v[i] in -99..99 (domain of IntVarArray)
- square of each number -> sq[i] == sqr(v[i]) via rel (sq domain 0..9801); sqr is a MiniModel arithmetic expression
- given in the description: A=16, B=2, F=8, G=14 -> rel(v[k], IRT_EQ, value) (problem data, not instance data)
- sum of squares of two adjacent numbers equals sum of squares of the two diametrically opposite -> rel(sq[i] + sq[i+1] == sq[i+5] + sq[i+6]) for i=0..4 (i+5 gives the same equation, so five suffice)
- branching: branch(*this, v, INT_VAR_SIZE_MIN(), INT_VAL_MIN()) (decision variables; sq is fixed by v)
- objective: none (satisfaction)
