# Plan: assignment_costs (Paramita)

- Assign people to 4 tasks -> x[i][j] Bool (task i to person j), 4 x 5.
- Each task must be assigned to exactly one person -> per task i: sum_j x[i][j] == 1.
- Not necessary to assign all people to a task -> each person takes at most one task: per person j: sum_i x[i][j] <= 1.
- Minimise the total cost -> sum over i,j of cost[i][j] * x[i][j], objective minimise.
- Output x as the 4 x 5 nested list of Bools.
