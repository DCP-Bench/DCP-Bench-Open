# csplib_009_perfect_square_placement

Pack squares of given sides into a base square exactly, without overlap.

- Instance inputs: `base`, `sides`. Outputs: `x_coords`, `y_coords`, one
  integer in 0..base per square.
- Satisfaction. Each square stays inside the base, and no two squares overlap.
  `disjoint2/1` states exactly the reference's pairwise disjunction.
