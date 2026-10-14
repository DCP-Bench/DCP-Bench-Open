Rounded distance has no sqrt in Essence': a letting comprehension with sum([ d | d : int(0..DMAX), (2d-1)^2 <= 4s, 4s < (2d+1)^2 ]) gives the rounded cost of each pair from the given coordinates.
Branching on a dist matrix and a free-domain dist variable (int(0..3000)) timed out on 20 cities; the precomputed COST letting with toInt(x) * COST as the objective did not.
A per-city cost channel (cityc[i] = sum_j x[i,j]*COST, cityc[i] >= min cost of row i) made the 20-city eil51 instance prove in about 20 s (before: timeout).
Still unproven on berlin52_first20 (20 cities) and eil76_first30 (30 cities) at 180 s; heuristic conflict and a column-minimum channel did not help. Retained with those two skipped.
