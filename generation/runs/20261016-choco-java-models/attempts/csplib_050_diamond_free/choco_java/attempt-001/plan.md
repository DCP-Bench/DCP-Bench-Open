Given a simple undirected graph G on N vertices -> symmetric 0/1 adjacency matrix x with zero diagonal (x[j][i] is the same variable as x[i][j]).
Each degree d_i > 0 and d_i modulo 3 -> d_i in {3,6,9,...} <= N-1, deg_i = sum of row i (m.sum(row, "=", d_i)).
Degree sequence d_1 >= ... >= d_N -> arithm(d_i, ">=", d_{i+1}).
Sum of degrees modulo 12 -> total = sum(d_i) = 12*k with k a new IntVar.
A diamond is four vertices with at least five edges between them; diamond-free -> for every 4-set, the 6 pair variables sum to <= 4 (m.sum(pairs, "<=", 4)).
Objective: none (satisfaction). Output the adjacency matrix.
