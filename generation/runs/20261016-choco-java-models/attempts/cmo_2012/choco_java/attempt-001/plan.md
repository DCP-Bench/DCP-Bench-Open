Problem: cmo_2012. Positive a, b with a - b prime, a*b = n^2 square, b > 0; minimise a with a >= min_a.
a in min_a..max_val (instance); b in 1..max_val; n in 1..max_val (n^2 = a*b <= max_val^2)
a - b = p, p in the primes up to max_val -> sum(b, p) = a
a * b = n * n -> times(a, b, sq) and times(n, n, sq)
Objective: minimise a. Outputs a, b, n, p.
