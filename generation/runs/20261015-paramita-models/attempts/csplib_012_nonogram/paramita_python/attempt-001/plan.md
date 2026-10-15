# Plan: csplib_012_nonogram (attempt-001)

Variables: shade[r,c] Bool per cell (1 = shaded). Each line (row or column) gets, per block k, a one-hot start s[k,t] and a prefix p[k,t] = block k starts at or before t.

- Each row/column lists its block lengths in order; 0 entries are padding and are skipped -> block lengths.
- Each block starts exactly once -> sum over t of s[k,t] == 1.
- Prefix chain -> p[k,t] <-> p[k,t-1] or s[k,t].
- Blocks in order with at least one gap -> s[k+1,t] implies p[k,t - len_k - 1].
- A cell is shaded when some block covers it -> cover[k,c] = p[k,c] and not p[k,c-len_k]; shade[c] <-> OR of covers.
- Lines with no blocks -> all cells unshaded.
- Objective: none (satisfaction). Output board = 1 * shade per cell.
