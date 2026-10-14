# Plan: coins_grid, attempt 1

- In a grid n by n, place coins: one Boolean per cell, x[i][j] = 1 if cell (i, j) holds a coin -> `BoolVarArray x(*this, n*n, 0, 1)`
- In each row exactly c coins must be placed -> `linear(*this, row_i, IRT_EQ, c, IPL_DOM)` for each row i
- In each column exactly c coins must be placed -> `linear(*this, col_j, IRT_EQ, c, IPL_DOM)` for each column j
- At most one coin can be placed in each cell -> the 0/1 domain of x (no extra post)
- The sum of the quadratic horizontal distance from the main diagonal of all cells containing a coin must be as small as possible -> `linear(*this, IntArgs(w), all_cells, IRT_EQ, z, IPL_BND)` with w[i*n+j] = (j-i)^2, z = total cost
- Branching: cells in ascending order of cost (ties by index), value 1 first (place the cheap coins first) -> `branch(*this, ordered, BOOL_VAR_NONE(), BOOL_VAL_MAX())`
- Objective: `minimize(z)`
