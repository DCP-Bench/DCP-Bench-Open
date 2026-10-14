% Job shop: every job is a chain of tasks, each on a given machine for a given
% time, run in order. A machine works on one task at a time and a task runs
% without interruption. Minimise the time at which the last task finishes.
include "globals.mzn";

% jobs_data[j, k] = [machine, duration] of task k of job j. Jobs may have
% different numbers of tasks, so the runner pads the rows with [0, 0], which is
% also a real task shape (machine 0): only the first jobs_data_len[j] tasks of
% job j are real.
array[int,int,int] of int: jobs_data;
array[int] of int: jobs_data_len;

set of int: Jobs = index_set(jobs_data_len);

% the real tasks as one flat list, job by job and in job order
array[int] of int: tj = [j | j in Jobs, k in 1..jobs_data_len[j]];   % job of the task
array[int] of int: tk = [k | j in Jobs, k in 1..jobs_data_len[j]];   % position in its job
set of int: Tasks = index_set(tj);
array[Tasks] of int: mach = [jobs_data[tj[t], tk[t], 1] | t in Tasks];
array[Tasks] of int: dur = [jobs_data[tj[t], tk[t], 2] | t in Tasks];
set of int: Machines = {mach[t] | t in Tasks};
int: mlo = min(Machines);
int: mhi = max(Machines);

% work of each job, and of each task's job before and from that task on
array[Jobs] of int: job_work = [sum(t in Tasks where tj[t] = j) (dur[t]) | j in Jobs];
array[Tasks] of int: before =
    [sum(u in Tasks where tj[u] = tj[t] /\ tk[u] < tk[t]) (dur[u]) | t in Tasks];
array[Tasks] of int: after = [job_work[tj[t]] - before[t] | t in Tasks];

% Lower bound on the makespan: no machine finishes before it has done all its
% work, and no job before all its tasks have run.
int: lower = max([sum(t in Tasks where mach[t] = m) (dur[t]) | m in Machines] ++ job_work);

% Upper bound (the horizon): the length of one feasible schedule, built by
% repeatedly starting, among the next unscheduled task of every job, the one that
% can start earliest (its job's previous task done and its machine free). The
% optimum is never longer. nxt, jready and mready are the next task of each job,
% when each job is free, and when each machine is free.
int: idle = sum(dur) + 1;   % later than any start in the greedy schedule
function int: greedy(array[int] of int: nxt, array[int] of int: jready,
                     array[int] of int: mready) =
    if forall(j in Jobs) (nxt[j] > jobs_data_len[j]) then max(jready)
    else let {
        array[int] of int: est =
            [if nxt[j] <= jobs_data_len[j]
             then max(jready[j], mready[jobs_data[j, nxt[j], 1]]) else idle endif | j in Jobs];
        int: s = min(est);
        int: j0 = min([j | j in Jobs where est[j] = s]);
        int: m0 = jobs_data[j0, nxt[j0], 1];
        int: e = s + jobs_data[j0, nxt[j0], 2];
    } in greedy([nxt[j] + bool2int(j = j0) | j in Jobs],
                [if j = j0 then e else jready[j] endif | j in Jobs],
                array1d(mlo..mhi, [if m = m0 then e else mready[m] endif | m in mlo..mhi]))
    endif;
int: horizon = greedy([1 | j in Jobs], [0 | j in Jobs], array1d(mlo..mhi, [0 | m in mlo..mhi]));

% start[t] = start time of task t; a task starts after the earlier tasks of its
% job and leaves room for the later ones before the horizon
array[Tasks] of var 0..horizon: start;
constraint forall(t in Tasks) (start[t] >= before[t] /\ start[t] <= horizon - after[t]);

% no task of a job can start until the previous task of that job has ended
constraint forall(t in Tasks where tk[t] > 1) (start[t] >= start[t - 1] + dur[t - 1]);

% a machine works on one task at a time: of any two tasks on the same machine,
% one ends before the other starts
constraint forall(a, b in Tasks where a < b /\ mach[a] = mach[b]) (
    start[a] + dur[a] <= start[b] \/ start[b] + dur[b] <= start[a]);

% The same rule again as one unary resource per machine, which Gecode propagates
% over all tasks of the machine at once rather than pair by pair. The strict form
% matches the pairwise rule above also for zero-length tasks.
constraint forall(m in Machines) (
    disjunctive_strict([start[t] | t in Tasks where mach[t] = m],
                       [dur[t] | t in Tasks where mach[t] = m]));

% Each task starts as early as its job and its machine order allow: at time 0
% (first task of a job), when the previous task of its job ends, or when another
% task on its machine ends. Moving tasks left this way never lengthens a
% schedule, so the optimal makespan, the only output, is unchanged; it removes
% the schedules that differ only by idle time before a task, which the runner
% would otherwise enumerate one by one after fixing the optimum.
constraint forall(t in Tasks) (
    (if tk[t] = 1 then start[t] = 0 else start[t] = start[t - 1] + dur[t - 1] endif)
    \/ exists(u in Tasks where u != t /\ mach[u] = mach[t]) (start[t] = start[u] + dur[u]));

% the makespan is when the last task of any job ends, to be minimised
var lower..horizon: makespan =
    max(t in Tasks where tk[t] = jobs_data_len[tj[t]]) (start[t] + dur[t]);
var int: objective = makespan;
solve minimize objective;

output ["{\"makespan\": ", show(makespan), "}"];
