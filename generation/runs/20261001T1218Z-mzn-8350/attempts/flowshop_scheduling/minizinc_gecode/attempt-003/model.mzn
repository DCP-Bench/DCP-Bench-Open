% Permutation flowshop: every job is processed on machines 1..M in that order,
% and all machines process the jobs in the same sequence. Choose the sequence
% of jobs so that the makespan (the time when every job has finished on the
% last machine) is as small as possible.
include "globals.mzn";

array[int] of int: jobs;                     % the jobs
array[int] of int: machines;                 % the machines, visited in this order
array[int, int] of int: process_time;        % process_time[j, m] = time of job j on machine m
array[int] of int: schedules;                % positions in the sequence (same as jobs); unused,
                                             % the sequence length is the number of jobs

set of int: Jobs = index_set_1of2(process_time);
set of int: Machines = index_set_2of2(process_time);
int: n_jobs = card(Jobs);
int: first_machine = min(Machines);
int: last_machine = max(Machines);
set of int: Positions = 1..n_jobs;

% every job is processed once, so the makespan cannot exceed the sum of all times
int: max_duration = sum(j in Jobs, m in Machines) (process_time[j, m]);

% sequence[k] = the job processed k-th
array[Positions] of var Jobs: sequence;

% every job appears exactly once in the sequence
constraint all_different(sequence);

% start[k, m], finish[k, m] = start and completion time on machine m of the
% job in position k of the sequence
array[Positions, Machines] of var 0..max_duration: start;
array[Positions, Machines] of var 0..max_duration: finish;

% processing takes the job's time on that machine
constraint forall(k in Positions, m in Machines)
    (finish[k, m] = start[k, m] + process_time[sequence[k], m]);

% A job starts on a machine as soon as it has finished on the machine before
% it and the previous job of the sequence has finished on this machine. Fixing
% the start this way (instead of only bounding it from below) is the usual
% flowshop timing of a sequence and leaves one schedule per sequence, so the
% search does not run through equivalent delayed schedules, which never
% lower the makespan.
constraint forall(k in Positions, m in Machines)
    (start[k, m] = max([0]
        ++ [finish[k, m2] | m2 in Machines where m2 = m - 1]
        ++ [finish[k2, m] | k2 in Positions where k2 = k - 1]));

% makespan = time at which the last job finishes on the last machine (the last
% job of the sequence finishes last on the last machine)
var 0..max_duration: makespan;
constraint makespan = finish[n_jobs, last_machine];

% Implied lower bound (removes no solution, helps Gecode prune): machine m must
% process all its jobs, cannot begin before the shortest time any job needs to
% reach it, and its last job still has to pass through the machines after it.
constraint forall(m in Machines)
    (makespan >= sum(j in Jobs) (process_time[j, m])
        + min(j in Jobs) (sum(m2 in Machines where m2 < m) (process_time[j, m2]))
        + min(j in Jobs) (sum(m2 in Machines where m2 > m) (process_time[j, m2])));

var int: objective = makespan;
solve minimize objective;

output ["{\"makespan\": ", show(makespan), "}"];
