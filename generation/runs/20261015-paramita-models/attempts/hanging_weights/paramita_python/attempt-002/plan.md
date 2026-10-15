# Plan: hanging_weights (attempt 002)

Each weight (A-M) is an integer 1..13 -> one-hot Bools per letter, exactly one value each.

Balance rule: weights on either side of a pivot, times their distance from the pivot, balance.
Pivot positions read from the diagram columns (distances in characters, divided by nothing).
Change from attempt 001: the bar holding H and I hangs from column 9 (the bar's '+' nearest the
drawn vertical at column 8), not column 8. Attempt 001 gave two solutions and the evaluator
found its output could not extend to the reference.

Top bar, hung at the stem (col 23): L-M bar (W2) at distance 12 left, J-K bar (W4) at distance 9 right.
-> 12 * W2 == 9 * W4, W2 = W3 + L + M, W4 = X + J + K + W6.

Bar of L and M (pivot col 11): H-I bar (W3) at distance 3 left, L at distance 3 right, M at distance 12 right.
-> 3 * W3 == 3 * L + 12 * M, W3 = H + I + W5.

Bar of H and I (pivot col 9): H at distance 9 left, E-F bar (W5) at distance 6 right, I at distance 9 right.
-> 9 * H == 6 * W5 + 9 * I, W5 = E + F.

Bar of E and F (pivot col 14): E at distance 9 left, F at distance 6 right.
-> 9 * E == 6 * F.

Bar of J and K (pivot col 32): A-B bar (X) at distance 8 left, J at distance 5 left,
K at distance 4 right, G bar (W6) at distance 7 right.
-> 8 * X + 5 * J == 4 * K + 7 * W6, X = A + B, W6 = G + Y.

Bar of A and B (pivot col 23): A at distance 12 left, B at distance 3 right.
-> 12 * A == 3 * B.

Bar of G (pivot col 38): G at distance 9 left, C-D bar (Y) at distance 6 right. Description: 3*G = 2*(C+D).
-> 9 * G == 6 * Y, Y = C + D.

Bar of C and D (pivot col 44): C at distance 15 left, D at distance 3 right. Description: 5*C = D.
-> 15 * C == 3 * D.

Objective: satisfaction, no objective. Outputs a..m are the weight values.
