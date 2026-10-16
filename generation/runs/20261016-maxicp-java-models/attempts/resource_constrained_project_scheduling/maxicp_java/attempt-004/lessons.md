# resource_constrained_project_scheduling, maxicp_java: lessons

Result: accepted on 3 of 5 instances (example, json:1, json:4). json:2 (optimum 53) and json:3 (optimum 79)
hit the 180 s limit with "Candidate optimum was not proven". 3/5 = 60% checked, below the 80% needed to retain.

What was tried (all attempts accepted the example, json:1, json:4; none proved json:2 or json:3):

- attempt-001 (earlier, time-indexed Boolean running variables with reified starts): json:2 and json:3 timed out.
- attempt-002 (cumulative with `makeIntervalVar(cp, false, d)`, `pulse` and `le` per resource, `endBeforeStart` for precedences, `start(t)` as outputs, `makespan(task)` as objective): same two timeouts. Free check fast, full run 372 s.
- attempt-003: adds implied bounds from the data: head and tail chains, the energy bound work/capacity per resource, `ge(makespan, LB)`, and `start + dur + tail <= makespan` per job. The first version used a latest start `LB - dur - tail` as a deadline; that is wrong (LB is a lower bound, not an upper bound on the makespan) and gave `no_solution` on the example. The corrected version still times out on json:2 and json:3.
- attempt-004: adds `noOverlap` for each pair of jobs whose needs of one resource add up to more than its capacity, on top of attempt-003. Same two timeouts.

Likely cause: the lower bounds stay well below the optimum on the 32-job instances (json:2: longest chain plus energy gives 41, optimum 53), and the driver's plain DFS (firstFailBinary, no learning, no restarts) must refute every makespan below the optimum. Propagation added here did not close that gap.

Not tried: a tighter horizon than the sum of durations (needs an implied bound, not a guess); a different encoding of the cumulative that the driver's branching may search better.
