# knights_tour, highs_cpp, attempt 003

Accepted, 4 of 5 instances checked (0.8), retained. 10x10 times out at 180 s.

- Arc formulation: binary arc[s][t] on knight moves, start[s] and last[s] markers, in/out degree 1 rows,
  integer pos[s] with pos[t] - pos[s] >= 1 - N(1 - arc[s][t]) (MTZ, rules out subcycles), pos = 0 on the start
  and N-1 on the last square. No fixed start square, no symmetry breaking.
- Far smaller than the time-indexed model of attempt 002 (n^2 + 8n^2 columns instead of ~n^4/2), and faster:
  8x8 first solution 77 s without a fixed start, both solutions in 97 s; 5x5 12 s, 6x6 22 s, 7x7 31 s.
- 10x10 not solved in 180 s.
