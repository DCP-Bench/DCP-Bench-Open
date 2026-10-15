Each task is assigned to exactly one person -> person[i] in 0..people-1, one-hot x[i][j] via channel(*this, x[i], person[i], 0, IPL_DOM)
it is not necessary to assign all people to a task; a person takes at most one task (assignment) -> distinct(*this, person, IPL_DOM)
the cost of a task is the entry of the person doing it -> element(*this, IntSharedArray(cost[i]), person[i], cost[i], IPL_DOM)
the total cost is minimised -> total = expr(*this, sum(cost)); minimize(total)
branching: regret on the task costs first (INT_VAR_REGRET_MIN_MAX, INT_VAL_MIN), then the persons (INT_VAR_SIZE_MIN, INT_VAL_MIN); x is fixed through channel
