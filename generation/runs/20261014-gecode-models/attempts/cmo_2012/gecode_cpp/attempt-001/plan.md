Reading of max_val: bounds a and b (a, b <= max_val); n <= max_val follows from n^2 = a*b. p is the prime a - b. Minimise a.
two positive integers a and b -> IntVar a, b in [1, max_val] (domains, no post)
b should be larger than 0 -> b domain starts at 1 (no post)
a no less than a given minimum -> a domain [min_a, max_val] (no post)
a - b is a prime number -> p in IntSet(primes <= max_val, sieved at runtime), rel(*this, a == b + p) (linear, bounds)
a x b is a perfect square n^2 -> ab = expr(*this, a*b); nn = expr(*this, n*n); rel(*this, ab == nn) (times, bounds; decomposition, no map row for a square product)
branching -> branch(a, INT_VAL_MIN) first, then n and b, then p (all decisions fixed)
objective: smallest a -> minimize(a)
