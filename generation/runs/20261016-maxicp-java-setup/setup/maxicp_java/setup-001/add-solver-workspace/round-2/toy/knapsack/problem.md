# 0/1 knapsack

Choose a subset of items whose total weight does not exceed the capacity, so
that the total value is as **large** as possible.

Instance: `{"weights": [...], "values": [...], "capacity": 15}`; item `i` has
weight `weights[i]` and value `values[i]`.

Print one optimal solution as `{"take": [t_0, ..., t_{n-1}]}`, where `t_i` is
1 if item `i` is taken and 0 otherwise.
