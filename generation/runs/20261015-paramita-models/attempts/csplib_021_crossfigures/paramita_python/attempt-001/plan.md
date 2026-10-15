Encoding: each white cell holds its digit as 4 binary Bools (value <= 9); one-hot digits timed out at 60 s in the quick check.
Each white cell holds one digit 0-9 -> 4 binary Bools per cell, sum of 2^k * bit <= 9; black cells output 0.
Each answer reads its cells left-to-right (across) or top-to-bottom (down) as a number -> value = sum 10^k * digit_k (PB linear integer expression).
Clue "A1: 27 across times two" -> A1 == 2 * A27
Clue "A4: 4 down plus seventy-one" -> A4 == D4 + 71
Clue "A7: 18 down plus four" -> A7 == D18 + 4
Clue "A8: 6 down divided by sixteen" -> 16 * A8 == D6
Clue "A9: 2 down minus eighteen" -> A9 == D2 - 18
Clue "A10: Dozen in six gross" -> A10 == 72 (6*144/12)
Clue "A11: 5 down minus seventy" -> A11 == D5 - 70
Clue "A13: 26 down times 23 across" -> A13 == D26 * A23; A23 is a 2-digit prime, so per prime p: If(A23 digits == p, A13 == p * D26)
Clue "A15: 6 down minus 350" -> A15 == D6 - 350
Clue "A17: 25 across times 23 across" -> A17 == A25 * A23; per prime p: If(A23 digits == p, A17 == p * A25)
Clue "A20: A square number" -> A20 is 4 digits; OR over the 4-digit squares of the digit match
Clue "A23: A prime number" -> A23 is 2 digits; OR over the 2-digit primes of the digit match
Clue "A24: A square number" -> A24 is 2 digits; OR over 16,25,36,49,64,81
Clue "A25: 20 across divided by seventeen" -> 17 * A25 == A20
Clue "A27: 6 down divided by four" -> 4 * A27 == D6
Clue "A28: Four dozen" -> A28 == 48
Clue "A29: Seven gross" -> A29 == 1008
Clue "A30: 22 down plus 450" -> A30 == D22 + 450
Clue "D1: 1 across plus twenty-seven" -> D1 == A1 + 27
Clue "D2: Five dozen" -> D2 == 60
Clue "D3: 30 across plus 888" -> D3 == A30 + 888
Clue "D4: Two times 17 across" -> D4 == 2 * A17
Clue "D5: 29 across divided by twelve" -> 12 * D5 == A29
Clue "D6: 28 across times 23 across" -> D6 == A28 * A23 = 48 * A23 (linear, A28 fixed)
Clue "D10: 10 across plus four" -> D10 == A10 + 4
Clue "D12: Three times 24 across" -> D12 == 3 * A24
Clue "D14: 13 across divided by sixteen" -> 16 * D14 == A13
Clue "D16: 28 down times fifteen" -> D16 == 15 * D28
Clue "D17: 13 across minus 399" -> D17 == A13 - 399
Clue "D18: 29 across divided by eighteen" -> 18 * D18 == A29
Clue "D19: 22 down minus ninety-four" -> D19 == D22 - 94
Clue "D20: 20 across minus nine" -> D20 == A20 - 9
Clue "D21: 25 across minus fifty-two" -> D21 == A25 - 52
Clue "D22: 20 down times six" -> D22 == 6 * D20
Clue "D26: Five times 24 across" -> D26 == 5 * A24
Clue "D28: 21 down plus twenty-seven" -> D28 == D21 + 27
Objective: none (satisfaction); outputs M[9][9] = digit of each cell, 0 for black cells.
