We want to climb a stair of n steps with a number of steps at a time, within a given range [m1, m2]. -> each move steps[k] is 0 or in [m1, m2]: (steps[k] = 0) or (steps[k] >= m1 and steps[k] <= m2); a running position pos[k+1] = pos[k] + steps[k] (sum)
Find a way to climb a stair of n steps (you can take only m1 to m2 steps at a time) -> pos[0] = 0, pos[20] = n, and every pos[k] <= n (domain), so the moves reach the top exactly without overshoot
or 0 if no steps are taken at that move, i.e. after we reach the top of the stair -> steps[k] = 0 iff pos[k] = n (reified equivalence)
Print the number of steps (steps) taken at each move as a list of 20 integers -> output steps (declared width 20)
Objective: satisfaction (no objective)
