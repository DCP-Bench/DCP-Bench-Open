Given two positive integers a and b
  -> a, b as binary numbers over bits: a = sum 2^i * A_i, b = sum 2^i * B_i; b >= 1
a - b is a prime number
  -> p as binary number; exactly one prime q chosen (one-hot P_q), If(P_q, p == q); a - b == p
a x b is a perfect square n^2
  -> n as binary number; products by column addition: partial products (A_i and B_j) summed per column with unary carries; result bits of a*b and of n*n are equal bit by bit
a is no less than the given minimum
  -> a >= min_a
a, b, n, p are bounded by the instance bound max_val
  -> a, b, n, p <= max_val; bit width is the bit length of max_val
Print a, b, n, p
  -> outputs as integer expressions
Objective: minimise a
  -> ("minimize", a)
