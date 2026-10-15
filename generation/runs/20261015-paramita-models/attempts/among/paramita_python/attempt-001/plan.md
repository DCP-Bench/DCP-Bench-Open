# Plan: among

Encoding: one-hot Bools X[i][d] (x[i] = d) for d in 0..7; value x[i] = sum(d * X[i][d]).
Membership in v: b_i = sum(X[i][d] for d in v) (0/1 expression).

- each entry x[i] takes exactly one value from 0..7 -> sum_d X[i][d] == 1
- exactly m values in x take one of the values in v -> sum_i b_i == m
- All other values may be anything in 0..7 -> no further constraint
- Objective: none (satisfaction); output x = [sum(d * X[i][d]) for i].
