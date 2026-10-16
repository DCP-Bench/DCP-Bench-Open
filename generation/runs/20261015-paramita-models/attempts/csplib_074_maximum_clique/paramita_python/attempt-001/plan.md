# Plan: csplib_074 maximum clique (binary vertex vector, maximise clique size)

- "a clique is a subset where every two distinct vertices are adjacent" -> for each non-adjacent pair (i, j), i < j: not (c_i and c_j)
- "c[i] is 1 if vertex i is in the clique" -> one Bool per vertex, output c as list of Bools
- "find a clique of the largest possible size" -> objective: maximise sum of c_i
