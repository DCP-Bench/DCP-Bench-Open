One common scheduling problem is the job shop, in which multiple jobs are processed on several machines.

Each job consists of a sequence of tasks, which must be performed in a given order, and each task must be processed
on a specific machine. For example, the job could be the manufacture of a single consumer item, such as an automobile.
The problem is to schedule the tasks on the machines so as to minimize the length of the schedule—the time it takes
for all the jobs to be completed.

There are several constraints for the job shop problem:
- No task for a job can be started until the previous task for that job is completed.
- A machine can only work on one task at a time.
- A task, once started, must run to completion.

Print the optimal makespan (makespan), which is the total time taken to complete all jobs.
