# Plan: flowshop_scheduling

- "find a sequence of jobs" -> one-hot x[j][p]: job j at sequence position p; `sum_p x == 1` per job, `sum_j x == 1` per position
- "time required to process job j on machine m is ProcesTime_{j,m}" -> P[p][m] = sum_j t[j][m] * x[j][p] (PB, weights up to max time)
- "the first job goes to the first machine" / "other jobs wait" -> C[p][m] >= C[p-1][m] + P[p][m] (job finishes on machine m after its previous machine finished)
- "when the first machine has processed the first job, the first job goes to the second machine" -> C[p][m] >= C[p][m-1] + P[p][m]
- completion times C[p][m] -> binary integers, upper bound = sum of all processing times (valid since makespan <= total work)
- "minimize the makespan: the time when all jobs have been processed" -> makespan = C[n-1][M-1], minimise
