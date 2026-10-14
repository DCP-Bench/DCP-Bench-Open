# Plan: csplib_028_bibd (v, b, r, k, lambda)

- the incidence matrix has v rows (objects) and b columns (blocks), 0/1 -> BoolVarArray x[i*b+c], output as vector<BoolVarArgs>, one list per row
- each object occurs in exactly r blocks -> linear(row_i, IRT_EQ, r)
- each block holds exactly k distinct objects -> linear(col_c, IRT_EQ, k)
- two distinct objects occur together in exactly lambda blocks -> per pair: m_c = expr(x_ic && x_jc) over blocks c, then linear(m, IRT_EQ, lambda)
- rows and columns are interchangeable (permuting objects or blocks keeps a design): double-lex, rel(row_i, IRT_LQ, row_i+1) and rel(col_c, IRT_LQ, col_c+1) (lex with Boolean arrays)
- branching: all cells, BOOL_VAR_AFC_MAX(0.99), BOOL_VAL_MIN(), with restarts(100) (heavy-tailed satisfaction search)
- sizes and r, k, lambda all from the instance; nothing typed in
