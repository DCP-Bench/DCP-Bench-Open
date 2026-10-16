Three coins lie on a table in the order tails, heads, tails. -> init fixed: steps[0][c] = init[c] (instance field init, 1 = tails)
In precisely three moves -> num_moves = 3 from the instance; states 0..3, so steps has num_moves+1 rows
make them face either all heads or all tails -> last state: all coins equal (arithm "=" between coins of the last row)
Each move consists of choosing one coin and flipping it over. -> between consecutive states exactly one coin differs: sum of reified "!=" per coin = 1
Print the steps (steps), True = tails -> output steps as BoolVar matrix [num_moves+1][3]
objective: none (satisfaction)
