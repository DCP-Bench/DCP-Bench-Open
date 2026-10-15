Interpretation: instance n bounds the number of digits (the number is below 10^n); the number is larger than 1, so the root is k >= 2.
A Dudeney number is a perfect cube -> number = cube of k, k in 2..K with K^3 < 10^n -> element(IntArgs(cubes), k, number) (table of cubes, domain consistent)
the sum of its digits is equal to the cube root -> sum(d) == k -> linear(*this, d, IRT_EQ, k)
the number is written in decimal digits d_0..d_{n-1} (0..9 each) -> number == sum(d_i * 10^i) -> linear(*this, IntArgs(pow10), d, IRT_EQ, 0) with number as a term (IntVar number in the sum)
branching: cube root k first (INT_VAR_NONE, INT_VAL_MIN), then the digits in order (determined mostly by propagation)
objective: none (satisfaction)
