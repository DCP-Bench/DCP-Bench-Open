all jobs go through the machines in the same order (permutation flow shop) -> distinct(*this, seq, IPL_DOM) over the position-to-job array seq, with element() per position and machine for the processing time (no map row for a permutation of jobs with a machine-dependent duration beyond element)
each machine processes one job at a time -> chain on completion times: done[k][i] >= done[k-1][i] + p(k,i) (a machine starts position k after position k-1 finishes); a job leaves machine i-1 before it starts on machine i -> done[k][i] >= done[k][i-1] + p(k,i). Chain is the unary resource with a fixed order, so no unary() is needed.
processing time of the job in position k on machine i -> element(IntArgs(column_i), seq[k]) [column_i read from the instance process_time]
branching -> seq first (INT_VAR_SIZE_MIN, INT_VAL_MIN), then the completion times (INT_VAR_NONE, INT_VAL_MIN)
objective -> makespan = completion time of the last position on the last machine; minimize
