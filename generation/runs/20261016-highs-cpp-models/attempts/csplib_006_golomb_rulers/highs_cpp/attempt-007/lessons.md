# csplib_006_golomb_rulers, highs_cpp: lessons (attempt-007)

Accepted, 4 of 5 instances checked (sizes 5, 7, 8, 9 proven in 8, 7, 19, 86 s; size 10 times out).
What moved size 9 from a timeout to 86 s:
- Domains and rows from shortest-ruler lower bounds G[k], computed in build by a small DFS for k < m
  (a_j - a_i >= G[j-i+1], a_k in [G[k+1], L - G[m-k]]); e[t][k] fixed to 0 outside the domain.
- Cumulative order rows: mark k at or before t implies mark k-1 at or before t-1.
- Dropping the window cuts (they cost more per node than they pruned): 178 s -> 102 s.
- 3-term arithmetic-progression rows x_t + x_{t+d} + x_{t+2d} <= 2: 102 s -> 94 s.
Did not help: product rows y <= x plus sum of all y = m(m-1)/2 (timeout), 4-point rows for
disjoint pairs with equal difference (timeout, 14k rows). No reflection symmetry break used.
