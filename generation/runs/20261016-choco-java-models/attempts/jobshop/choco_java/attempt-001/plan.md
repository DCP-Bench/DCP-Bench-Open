One common scheduling problem is the job shop, multiple jobs processed on several machines. -> one start variable per task, tasks grouped by machine
Each job consists of a sequence of tasks, which must be performed in a given order -> precedence: start[j][k-1] + dur[j][k-1] <= start[j][k]
each task must be processed on a specific machine -> task (j,k) belongs to machine mach[j][k]
No task for a job can be started until the previous task for that job is completed. -> precedence chain per job
A machine can only work on one task at a time. -> m.cumulative(tasks of machine, unit heights, capacity 1) per machine
A task, once started, must run to completion. -> fixed duration taskVar(start, dur)
minimize the length of the schedule -> makespan >= start[j][last] + dur for every job, MINIMIZE makespan
