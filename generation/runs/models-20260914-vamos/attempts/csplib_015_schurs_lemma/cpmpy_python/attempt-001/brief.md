# csplib_015_schurs_lemma

Put balls 1..n into c boxes so that no triple (x, y, z) with x + y = z lies
entirely in one box.

- Instance inputs: `n` (balls), `c` (boxes).
- Output: `balls` — n integers in 1..c.
- Satisfaction. For every x in 1..n-1, y in 1..n-x with z = x + y <= n:
  the three balls x, y, z are not all in the same box (x = y is included).
