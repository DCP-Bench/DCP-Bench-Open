Attempt 001 wrote the capacity constraint over `index_set(weights)`, which is
1..n, while the reference's bin indices are 0-based: bin 0 was therefore never
constrained and could overflow. Attempt 002 ranges over 0..n-1, the same indices
the reference uses.
