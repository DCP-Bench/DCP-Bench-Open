# cmo_2012 lessons (cvc5_python)

- attempt-001: a * b == n * n with unknowns a, b, n, p. Accepted on 1 of 5 instances (instances_checked 1/5); the other four timed out in the optimality proof at 180 s.
- attempt-002: added redundant s, t with a = s*s, b = t*t, n = s*t, still nonlinear. Accepted on 1 of 5 (json:1 fast, json:2 found a solution but timed out proving it, json:3 and json:4 timed out). Products of two unknowns stay too slow for cvc5 here.
- attempt-003: same square roots written as lookup tables over s and t (If(s == k, k*k, 0)), so every term is linear. Accepted on 4 of 5 (example timed out at 180 s; json:1 1 s, json:2 8 s, json:3 24 s, json:4 44 s). Retained at 0.8.
- The square-root step is a reasoning shortcut: a - b prime and a * b square force a and b to be squares when b > 0. The lookup tables carry that fact. The reference does not need it.
- The example instance (min_a 2012, max_val 10000) still times out. The model is retained at the 0.8 threshold, not at full coverage.
