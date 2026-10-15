# Plan: pythagorean_triplet
a, b, c are natural numbers -> unary (order) bits, value = sum of the bits, lower bound 1 by a forced first bit
a < b < c (three natural numbers, a < b < c) -> sum(a) + 1 <= sum(b), sum(b) + 1 <= sum(c)
a + b + c = 1000 (the triplet sums to 1000) -> sum(a) + sum(b) + sum(c) == 1000 (unit-weight PB)
a^2 + b^2 = c^2 -> each square is a 20-bit binary number fixed by implications on the exact unary value (v -> bits of v*v); the binary squares satisfy sq_a + sq_b == sq_c (small-weight PB, avoids weighted PB over unary bits, which ran out of memory)
Bounds from a < b < c and a + b + c = 1000: a <= 332, b <= 499, c <= 998
Objective: none (satisfaction); outputs a, b, c as integer expressions
