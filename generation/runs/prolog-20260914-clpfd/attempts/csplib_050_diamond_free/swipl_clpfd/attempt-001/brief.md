# csplib_050_diamond_free

A simple undirected diamond-free graph on N vertices whose degrees are positive
multiples of 3 and whose degree sum is a multiple of 12.

- Instance input: `N` (an uppercase key). Output: `matrix` — the N x N adjacency
  matrix, Booleans written as 0/1.
- Satisfaction. Row sums positive and divisible by 3; whole-matrix sum divisible
  by 12; zero diagonal; symmetric; every four vertices span at most four of
  their six edges.
