Participants are assigned to cars, each participant is interested in a subset of cars, and the goal is to maximize the total number of assignments.
Each participant is assigned to at most one car -> m.sum(row_i, "<=", 1) over the participant's row of assignment Booleans.
Each car is assigned to at most one participant -> m.sum(col_j, "<=", 1) over the car's column of assignment Booleans.
Assignments only where the participant is interested in the car (possible_assignments[i][j] = 1) -> pairs not of interest are fixed to 0 with arithm(x, "=", 0).
Objective: maximize the total number of assignments -> m.sum("total", all Booleans), setObjective(MAXIMIZE).
