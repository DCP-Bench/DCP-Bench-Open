In a quadratic grid n by n, one should place coins -> x[i][j] Bool per cell (one Bool per cell, so at most one coin per cell)
In each row exactly c coins must be placed -> sum of x[i][j] over j == c for each row i
In each column exactly c coins must be placed -> sum of x[i][j] over i == c for each column j
Sum of the quadratic horizontal distance from the main diagonal of all cells containing a coin must be as small as possible -> z = sum of (i-j)^2 * x[i][j], objective minimize z
Output x as the n by n Bool grid, output z as the integer expression of the objective
