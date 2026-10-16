The resource-constrained project scheduling problem involves scheduling a set of jobs, each with a specific duration and resource requirement.
  -> start[i] IntVar per job, domain 0..horizon (horizon = sum of durations); duration d_i
such that the total project duration (makespan) is minimized.
  -> makespan = max over jobs of start[i] + d_i (m.max), objective MINIMIZE
Each job may have precedence constraints, meaning certain jobs must be completed before others can start.
  -> for each successor link [pred, succ]: start[succ] - start[pred] >= d_pred (arithm with "-" and ">=")
there are multiple types of resources, each with a limited capacity that must not be exceeded at any time.
  -> for each resource r: cumulative(start, dur, need[.][r], capacity[r])
determine the start times of the jobs that minimize the makespan while satisfying all constraints.
  -> output start_time = start
Print the start times of the jobs (start_time) as a list of integers starting from 0.
  -> start domains from 0; output IntVar[] start
