Knight's tour on an n x n board: visit every square once, move numbers 0..n*n-1 (no return to start).
- the tour is represented by integers from 0 to n*n-1 -> cells indexed i*n+j, moves in rank[c] in 0..N-1 (N = n*n)
- a knight's tour is a sequence of knight moves -> circuit(*this, succ) over N+1 nodes, node N is a dummy closing the open path (open tour, no return to start); succ[c] in knight neighbours of c, or N (path end)
- the dummy node N's successor is the start square -> rank[start] = 0: rel((succ[N] == c) >> (rank[c] == 0)) for each c
- move numbers follow the path: each step adds one -> rank[succ[c]] == rank[c] + 1 unless succ[c] == N (element over rank with the dummy entry appended)
- every square visited exactly once -> circuit over succ (no separate distinct needed; ranks are distinct because they increase along the single circuit)
- the output x[i][j] = rank[i*n+j] -> Matrix over the rank array
- branching: succ first, fewest options first (Warnsdorff-like), then rank
- objective: none (satisfaction)
