# Plan: dudeney_numbers (instance field n = maximum number of digits)

- "a positive integer that is a perfect cube" -> the root r is one-hot over 2..9n (r >= 2 so the number is larger than 1; 9n bounds the digit sum, so it bounds r). The number is r^3 = sum_r r^3 * R[r].
- "at most n digits" -> n digit positions, each holding exactly one digit (one-hot d[p][v]).
- "the sum of its digits is equal to the cube root of the number" -> sum of all digits == sum_r r * R[r].
- "the number" -> number = sum_p 10^p * digit_p, and it equals r^3 (value constraint).
- Objective -> satisfaction; output number (int).
