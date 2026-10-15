# Plan: twelve_pack, attempt-001

Requirement: given a target number of items, find the closest combination of packs of different sizes that meets or exceeds the target.
-> total beers = sum_i packs[i] * count_i >= target, with count_i unary over ub_i = ceil(target/packs[i]) (Bool ge_i_k = count_i >= k, If(ge_i_(k+1), ge_i_k)); count_i = sum_k ge_i_k.

Requirement: print the counts of each pack size used (counts) as a list of integers.
-> outputs counts = [sum_k ge_i_k for each pack i], integer expressions.

Objective: closest means the smallest total that still meets the target.
-> minimize W, where W = sum_i packs[i] * count_i (same expression as the total).

Bounds: ub_i = ceil(target/packs[i]) is safe: an optimal solution never has more packs of size i than that, since dropping one pack would still meet the target and lower the total.
