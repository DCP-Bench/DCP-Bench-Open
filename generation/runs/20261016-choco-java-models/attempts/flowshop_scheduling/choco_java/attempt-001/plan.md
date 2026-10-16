# Plan: permutation flow shop, minimise makespan (flowshop_scheduling)

Jobs and machines from the instance; process_time[j][k] is the time of job j on machine k.
The description asks for the sequence minimising the makespan, so the job order is a decision (the field "schedules" is the reference's listed order and is not used).

- A sequence of all jobs, one job per position -> seq[p] in 0..n-1, m.allDifferent(seq, "AC")
- The time job at position p needs on machine k -> dur[p][k] = m.element(dur, column_k, seq[p]) (column_k = process_time of machine k)
- Machines process the jobs in the same order, one job at a time: the job at position p on machine k ends before the job at position p+1 on machine k starts -> start[p][k] + dur[p][k] <= start[p+1][k]
- All jobs go through the machines in order 1..M: the job at position p ends on machine k before it starts on machine k+1 -> start[p][k] + dur[p][k] <= start[p][k+1]
- The makespan is the time when all jobs have been processed: the last job's end on the last machine -> makespan = start[n-1][M-1] + dur[n-1][M-1]
- Horizon for domains: sum of all processing times.
- Objective: MINIMIZE makespan.
