# csplib_050_diamond_free

Find a simple undirected diamond-free graph on N vertices whose degrees are all
positive multiples of 3 and whose degree sum is a multiple of 12.

- Instance input: `N`.
- Output: `matrix` — N x N adjacency matrix of Booleans (0/1 is accepted).
- Satisfaction. Constraints: every row sum > 0 and divisible by 3; the whole
  matrix sum divisible by 12; zero diagonal; symmetry; and for every four
  vertices, at most four of the six possible edges are present.
