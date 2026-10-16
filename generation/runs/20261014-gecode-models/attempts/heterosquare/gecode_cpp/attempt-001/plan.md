Heterosquare of order n: an n*n square of distinct integers from 1 to n^2 whose row, column and diagonal sums are all different.
- the elements of the square are distinct integers from 1 to n^2 -> distinct(*this, cells, IPL_DOM) over the n*n cells with domain 1..n^2
- the sums of the rows, columns and diagonals are all different -> row sums, column sums and the two diagonal sums are linked to the cells by linear(sum) and then distinct(*this, sums, IPL_DOM) over all 2n+2 sums (sum bounds from n(n+1)/2 to n^3 - n(n-1)/2)
- print the square x as a list of rows -> output("x", rows) with one list per row
- branching -> INT_VAR_AFC_SIZE_MAX(0.99) over the cells only (sums are fixed once the cells are), INT_VAL_MIN, with restarts(100)
- objective -> none (satisfaction)
