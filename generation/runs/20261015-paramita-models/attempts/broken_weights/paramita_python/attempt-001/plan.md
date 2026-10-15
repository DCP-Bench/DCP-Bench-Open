A measuring weight broke into n pieces; each piece weighs a whole number of pounds -> one-hot Bool x[i][v] for v in 1..m, exactly one per piece, w_i = sum v*x[i][v]
the pieces weigh together the whole weight m -> sum(w_i) == m
the pieces could be used to weigh every integral weight between 1 and the total weight -> for each t in 1..m, a balance placement: reach DP over signed sums, reach[i][s] -> reach[i-1][s] | OR_v (x[i][v] & (reach[i-1][s-v] | reach[i-1][s+v])), reach[0][0] true, reach[n][t] true for t in 1..m
(instance note: the reference's all-different rule, pieces have distinct weights) -> w_i < w_{i+1} (strict order on the integer expressions)
Objective -> satisfaction, no objective (outputs: weights = [w_1..w_n])
