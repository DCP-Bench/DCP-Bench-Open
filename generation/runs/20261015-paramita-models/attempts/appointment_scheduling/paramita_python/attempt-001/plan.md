# Plan: appointment_scheduling (4 people, 4 slots, free-busy matrix m)

- Schedule 4 people into 4 interview slots -> x[i][j] Bool, person i in slot j; no integer encoding needed.
- Each person is assigned to exactly one slot -> per person i: sum_j x[i][j] == 1 (PB exactly-one).
- Each slot holds exactly one person -> per slot j: sum_i x[i][j] == 1 (PB exactly-one).
- Person i can only take a slot they are free in (m[i][j] = 1) -> per busy pair with m[i][j] = 0: ~x[i][j].
- Objective: none, satisfaction problem.
