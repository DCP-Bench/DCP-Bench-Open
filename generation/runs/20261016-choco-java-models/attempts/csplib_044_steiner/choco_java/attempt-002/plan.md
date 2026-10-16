ternary Steiner problem of order n -> instance field n, read via inst.getInt("n")
finding a set of n(n-1)/6 triples -> b = n(n-1)/6 rows, sets[i][j] BoolVars (row i is a triple, column j an element)
triples of distinct integer elements -> each row has exactly 3 true cells: m.sum(row, "=", 3)
any two triples have at most one common element -> for each element pair (j, l), at most one triple contains both: p[i] = sets[i][j] * sets[i][l] (m.times), sum over i of p[i] <= 1
implied: b triples cover 3b = n(n-1)/2 pairs, which is every pair once -> for each pair (j, l), sum over i of p[i] = 1
implied: every element lies in (n-1)/2 triples (its n-1 partners, two per triple) -> m.sum(column j, "=", (n-1)/2)
Print the set of triples as a boolean matrix -> out.put("sets", sets)
Search: dom/wdeg on the sets with Luby restarts (the first attempt timed out at n=13)
Objective: none (satisfaction)
