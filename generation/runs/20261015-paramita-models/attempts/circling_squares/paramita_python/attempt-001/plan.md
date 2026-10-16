Circling the squares: ten squares A..K on a circle (order A B C D E F G H I K), each a different number. Fractions not allowed, no number needs more than two figures -> whole numbers 0..99 (assumption).
-> one-hot integer per square: xv[p][v] Bool, sum(xv[p]) == 1; value = sum(v * xv[p][v]).
Different number in each square -> per value v: sum over squares of xv[p][v] <= 1.
The four example numbers stand: A=16, B=2, F=8, G=14 (problem constants) -> value == c.
Square of each number -> 14-bit binary sq[p] per square; If(xv[p][v], bit_k == bit k of v*v) for every v, k (weighted sum of v*v over one-hot crashes the encoder with exit 139 at 0..99).
Sum of squares of two adjacent numbers equals sum of squares of the two opposite numbers -> for edge (i, i+1) and opposite edge (i+5, i+6): sq[i] + sq[i+1] == sq[i+5] + sq[i+6], i = 0..4.
Objective: none (satisfaction); outputs A..K = value expressions.
