Problem: knapsack. Choose which items to take (x[i] true or false) so the total weight stays within the capacity and the total value is maximal.

- each item is taken or not -> BoolVar x[i] (output x as booleans)
- the total weight of the items taken does not exceed the capacity -> m.knapsack(x, weightSum, valueSum, weights, values), weightSum <= capacity
- total value of the items taken -> valueSum (from the knapsack global)
- objective: maximise total value -> m.setObjective(Model.MAXIMIZE, valueSum)
- output x -> out.put("x", x)
