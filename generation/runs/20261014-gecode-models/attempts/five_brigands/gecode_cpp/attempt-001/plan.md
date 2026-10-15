# Plan: five_brigands (Gecode, attempt-001)

Variables: A, B, C, D, E in 1..200 (each at least 1; the total bound of 200 caps each at 200).
- "the five brigands captured altogether exactly 200 doubloons" -> sum(A..E) == 200 -> linear(*this, IntArgs(1,1,1,1,1), x, IRT_EQ, 200)
- "if Alfonso had twelve times as much, Benito three times, Carlos the same, Diego half, Esteban one-third, still 200" -> 12A + 3B + C + D/2 + E/3 == 200, multiplied by 6 to stay in integers: 72A + 18B + 6C + 3D + 2E == 1200 -> linear(*this, IntArgs(72,18,6,3,2), x, IRT_EQ, 1200) [IPL default bounds; the fractions are cleared by the factor 6]
- "no brigand had less than one doubloon" -> domain lower bound 1 on each variable.
- Branching: all five are decision variables -> branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN()).
- Objective: none (satisfaction).
