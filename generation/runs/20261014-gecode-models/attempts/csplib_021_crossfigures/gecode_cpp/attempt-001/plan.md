# Plan: csplib_021_crossfigures (Gecode)

Grid: 9x9 cells, digits 0..9 in cell[9r+c]; black cells (X) fixed to 0 -> cell == 0.
Coordinates below are (row, column), 1-based, as in the description.

- every maximal run of white cells read left to right is a number with no leading zero -> number(cells): digits linked to value by linear(weights 10^k, digits, IRT_EQ, value), value domain 10^(L-1)..10^L-1
- every maximal run read top to bottom is a number likewise (same helper), so each cell is shared by its across and down entry
- 18 across and 18 down entries, one value variable each, lengths from the grid
- across 1 "27 across times two" -> A1 == 2 * A27 (rel with linear mult by constant)
- across 4 "4 down plus seventy-one" -> A4 == D4 + 71
- across 7 "18 down plus four" -> A7 == D18 + 4
- across 8 "6 down divided by sixteen" -> D6 == 16 * A8 (exact division)
- across 9 "2 down minus eighteen" -> A9 == D2 - 18
- across 10 "dozen in six gross" = 6*144/12 -> A10 == 72
- across 11 "5 down minus seventy" -> A11 == D5 - 70
- across 13 "26 down times 23 across" -> A13 == D26 * A23 (rel with product)
- across 15 "6 down minus 350" -> A15 == D6 - 350
- across 17 "25 across times 23 across" -> A17 == A25 * A23
- across 20 "a square number" (4 digits) -> s20 in 32..99, s20 * s20 == A20
- across 23 "a prime number" (2 digits) -> A23 domain = two-digit primes
- across 24 "a square number" (2 digits) -> s24 in 4..9, s24 * s24 == A24
- across 25 "20 across divided by seventeen" -> A20 == 17 * A25 (exact)
- across 27 "6 down divided by four" -> D6 == 4 * A27 (exact)
- across 28 "four dozen" = 48 -> A28 == 48
- across 29 "seven gross" = 7*144 -> A29 == 1008
- across 30 "22 down plus 450" -> A30 == D22 + 450
- down 1 "1 across plus twenty-seven" -> D1 == A1 + 27
- down 2 "five dozen" -> D2 == 60
- down 3 "30 across plus 888" -> D3 == A30 + 888
- down 4 "two times 17 across" -> D4 == 2 * A17
- down 5 "29 across divided by twelve" -> A29 == 12 * D5 (exact)
- down 6 "28 across times 23 across" -> D6 == A28 * A23
- down 10 "10 across plus four" -> D10 == A10 + 4
- down 12 "three times 24 across" -> D12 == 3 * A24
- down 14 "13 across divided by sixteen" -> A13 == 16 * D14 (exact)
- down 16 "28 down times fifteen" -> D16 == 15 * D28
- down 17 "13 across minus 399" -> D17 == A13 - 399
- down 18 "29 across divided by eighteen" -> A29 == 18 * D18 (exact)
- down 19 "22 down minus ninety-four" -> D19 == D22 - 94
- down 20 "20 across minus nine" -> D20 == A20 - 9
- down 21 "25 across minus fifty-two" -> D21 == A25 - 52
- down 22 "20 down times six" -> D22 == 6 * D20
- down 26 "five times 24 across" -> D26 == 5 * A24
- down 28 "21 down plus twenty-seven" -> D28 == D21 + 27
- branching: cells with INT_VAR_SIZE_MIN, INT_VAL_MIN; then the two square roots s20, s24
- objective: satisfaction; output M as Matrix<IntVarArray> (9 rows of 9)
