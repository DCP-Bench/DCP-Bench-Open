# Plan: hanging_weights (attempt 001)

Each weight (A-M) is an integer 1..13 -> one-hot Bools per letter, exactly one value each.

Balance rule: weights on either side of a pivot, times their distance from the pivot, are equal.
Pivot positions read from the diagram columns (offsets in characters):

Top bar, hung at the stem: left bar (L, M, H, I, E, F subtree) at distance 12, right bar (J, K, A, B, C, D, G subtree) at distance 9.
-> 12 * W2 == 9 * W4, where W2 = W3 + L + M and W4 = X + J + K + W6.

Bar of L and M (pivot under the top bar, col 11): left bar (H, I, E, F subtree) at distance 3, L at distance 3, M at distance 12.
-> 3 * W3 == 3 * L + 12 * M, where W3 = H + I + W5.

Bar of H and I (pivot col 8): H at distance 8, I at distance 10, bar E-F at distance 7 (right side).
-> 8 * H == 7 * W5 + 10 * I, with W5 = E + F.

Bar of E and F (pivot col 14): E at distance 9, F at distance 6.
-> 9 * E == 6 * F.

Bar of J and K (pivot col 32): bar X (A, B) at distance 8, J at distance 5, K at distance 4 (right), bar G-C-D at distance 7 (right).
-> 8 * X + 5 * J == 4 * K + 7 * W6, with X = A + B and W6 = G + Y.

Bar of A and B (pivot col 23): A at distance 12, B at distance 3.
-> 12 * A == 3 * B.

Bar of G (pivot col 38): G at distance 9, bar C-D at distance 6.
-> 9 * G == 6 * Y, with Y = C + D (the description's 3*G = 2*(C+D)).

Bar of C and D (pivot col 44): C at distance 15, D at distance 3.
-> 15 * C == 3 * D (the description's 5*C = D).

Objective: satisfaction, no objective. Outputs a..m are the weight values.
