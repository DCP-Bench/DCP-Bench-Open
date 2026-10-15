# Plan: resource_constrained_project_scheduling
Horizon H = sum of all job durations (a valid upper bound on the makespan), from the instance
each job starts at a time in 0..H -> unary (order) bits g[j][t] = "start of job j is at least t", g[j][0] true, g[j][H+1] false
each job has a fixed duration -> run[j][t] (job j is in progress at time t) <-> start_j in [t-d_j+1, t], from two order bits
each job has resource needs -> at each time t and resource r: sum_j need[j][r] * run[j][t] <= capacity[r] (weighted PB)
precedence (pred finishes before succ starts) -> start_succ >= start_pred + duration_pred: for each t, g[pred][t] -> g[succ][min(t+d, H+1)]
the dummy sink is the last job with duration 0 -> makespan = start of the sink
Objective: minimise the makespan (start of the sink = sum of its order bits)
Outputs: start_time[j] = sum of the order bits of job j
