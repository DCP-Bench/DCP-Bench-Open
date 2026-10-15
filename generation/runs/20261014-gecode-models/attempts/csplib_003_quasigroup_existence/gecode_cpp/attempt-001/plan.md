order m quasigroup: an m x m table, each symbol once per row and per column -> each row distinct, each column distinct (IPL_DOM)
each element occurs once in every row and column -> distinct(*this, row_i, IPL_DOM) and distinct(*this, col_j, IPL_DOM)
(a*b)*(b*a) = a for all a, b -> with c = Q[a][b], d = Q[b][a], element(*this, flat, d, m, c, m, const a, IPL_DOM) [flat[c*m+d] = a]
values 0..m-1 -> IntVarArray Q(*this, m*m, 0, m-1); m read from the instance
branching over the table -> branch(*this, Q, INT_VAR_SIZE_MIN(), INT_VAL_MIN())
objective -> none (satisfaction); output "quasigroup" as the m x m matrix
