arrangement of v distinct objects into b blocks -> matrix[v][b] of 0/1 incidence
each block contains exactly k distinct objects -> column sums = k
each object occurs in exactly r different blocks -> row sums = r
every two distinct objects occur together in exactly lambda blocks -> for each pair of rows, sum of AND of the two rows = lambda (products via addClausesBoolAndArrayEqVar)
objective: none (satisfaction); output matrix[v][b]
