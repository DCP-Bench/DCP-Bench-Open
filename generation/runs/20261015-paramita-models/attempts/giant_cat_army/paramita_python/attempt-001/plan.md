# Plan: giant_cat_army (attempt-001)

Position i of the list holds one value (one-hot p[i][v], v in 0..60). Step i (element i -> i+1)
uses exactly one of add 5, add 7, take the square root (op[i][k]).

- "build this list by using one of three operations" -> sum_k op[i][k] == 1 per step; per value v and op k: If(p[i][v] & op[i][k], p[i+1][v+5] / v+7 / isqrt(v)), or ~(p[i][v] & op[i][k]) when that result would be out of range or not an integer
- "starting with [0]" -> p[0][0]
- "ending with 14" and "length of 24" -> 24 positions, p[23][14]
- "all the elements are distinct" -> sum_i p[i][v] <= 1 per value
- "they're all <=60" -> one-hot over 0..60 only
- "all only integers" -> one-hot values, sqrt only on perfect squares
- "2, 10 and 14 appear on the list, in that order" -> sum_i p[i][2] == 1, sum_i p[i][10] == 1, If(p[j][10], some earlier p[i][2])
- objective: none (satisfaction); output x = integer value of each position (PB sum v * p[i][v])
