a simple undirected graph on N vertices, no loop edges -> one Bool per unordered pair {u,v} (edge), mirrored into the symmetric matrix; diagonal Bools forced false
each degree d_v is greater than zero and modulo 3 (read as: divisible by 3) -> d_v = sum of its edge Bools == 3 * q_v with q_v unary (q_v >= 1 forces d_v > 0)
degrees ordered d_i >= d_{i+1} -> PB comparison of the two incident-edge sums (symmetry breaking)
sum of the degrees is modulo 12 (|E| modulo 6) -> sum of all degrees == 12 * t with t unary (bounded by N(N-1)/12)
diamond is a set of four vertices with at least five edges between them; diamond-free means every 4-set has at most four edges -> for every 4-subset, sum of its six edge Bools <= 4
Objective -> satisfaction (none)
