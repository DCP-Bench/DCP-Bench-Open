# All optimal 0/1 knapsack selections

Choose a subset of items whose total weight does not exceed the capacity, so
that the total value is as **large** as possible. Several subsets can reach
the best value; find **every** one of them.

Instance: `{"weights": [...], "values": [...], "capacity": 4}`; item `i` has
weight `weights[i]` and value `values[i]`.

Print each optimal solution on its own line as `{"take": [t_0, ..., t_{n-1}]}`,
where `t_i` is 1 if item `i` is taken and 0 otherwise. Print every distinct
optimal solution exactly once, no solution that is not optimal, and nothing
else that starts with `{`.
