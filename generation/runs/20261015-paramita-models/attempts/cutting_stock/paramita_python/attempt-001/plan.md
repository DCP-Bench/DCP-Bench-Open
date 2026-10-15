number of times each cutting pattern is used -> unary integer per pattern: ge[p][i] = "x_p >= i+1", x_p = sum(ge[p]), chain If(ge[p][i+1], ge[p][i]), ub = max(1, sum(orders))
for each width, the total number of rolls cut meets the total Orders -> sum(num_rolls_width[p][w] * b for p, b in unary bits of x_p) >= orders[w] (PB, weights are the pattern counts)
minimize the total number of raw rolls cut -> objective sum of all unary bits (sum of x_p), ("minimize", total)
min_rolls_cut output -> total (the objective expression)
patterns_used output -> [x_p for each pattern p] as integer expressions
