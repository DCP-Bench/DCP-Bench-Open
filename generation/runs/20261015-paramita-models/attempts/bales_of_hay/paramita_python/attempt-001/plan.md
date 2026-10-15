# Plan: bales_of_hay (Paramita, one-hot bales, matching pairs to weights)

Bales b_0..b_{n-1} in 0..W, W = max(weights); one-hot Bool block x[i][v] per bale, b_i = sum v * x[i][v] (v >= 1).

- "a number of bales of hay" -> each bale takes exactly one value: `sum(x[i]) == 1`.
- "weighed in all possible combinations of two" -> one pair (i, j) per combination, i < j, n(n-1)/2 in all.
- "the weights of each of these combinations were written down ... without keeping track of which weight matched which pair" -> each pair is matched to one listed weight: y[pair][k] = 1 iff the pair's sum is weights[k]; `sum_k y == 1` per pair and `sum_pairs y == 1` per weight (a bijection between pairs and listed weights).
- "the weight of the pair is the sum of the two bales" -> `y[pair][k] <-> OR_a (x[i][a] & x[j][w_k - a])`.
- "weights ... in numerical order" -> no constraint on the order of the weights (they are a multiset).
- symmetry: the bales are printed in ascending order -> `b_i <= b_{i+1}` (the reference convention is sorted bales).
- objective: none (satisfaction); outputs: bales = [b_0 .. b_{n-1}] as integer expressions.
