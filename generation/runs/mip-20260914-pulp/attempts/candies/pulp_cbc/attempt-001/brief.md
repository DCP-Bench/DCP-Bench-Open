# candies
Instance: `ratings`. Outputs: `z` (total candies, 1..n*n) and `x` (1..n per
child). Minimize the total; a child rated above its left neighbour gets strictly
more candies, and strictly fewer when rated below. `z >= n` as in the reference.
