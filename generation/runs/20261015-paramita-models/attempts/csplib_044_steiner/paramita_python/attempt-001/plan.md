Set of n(n-1)/6 triples of distinct elements from {1..n} -> b = n(n-1)//6 triples, each a row of Bools X[t][e]
Each triple has distinct elements -> exactly 3 Bools true per row: sum(X[t]) == 3
Any two triples have at most one common element -> for t<s: sum_e (X[t][e] & X[s][e]) <= 1 (aux Bools)
Every pair of elements lies in exactly one triple (implied by count and the rule above) -> redundant: for each i<j, sum_t (X[t][i] & X[t][j]) == 1
Print the set of triples as a boolean matrix (rows triples, columns elements) -> output sets = X
Objective: satisfaction (no objective)
