Attempt 001 was accepted but Gecode hit the 180 s execution timeout on n = 16
and n = 20. Attempt 002 keeps the same solution set and pins the two halves to
the totals every solution must have: the all-different constraint over x and y
already forces them to partition 1..n, so sum(x) = sum(1..n)/2 and
sum(x^2) = sum of squares of 1..n over 2. Both are written multiplied out, so no
division is assumed to be exact.
