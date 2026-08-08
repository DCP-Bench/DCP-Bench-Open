
include "globals.mzn";

% Input data
int: n_jobs = 3;                  % Number of jobs
int: max_tasks = 3;               % Maximum number of tasks in any job
array[1..n_jobs] of int: num_tasks = [3, 3, 2];  % Number of tasks per job
int: n_machines = 3;              % Number of machines

% Machines are 1-based here. Original machine IDs 0,1,2 have been shifted to 1,2,3.
array[1..n_jobs, 1..max_tasks] of int: machine = 
  array2d(1..n_jobs, 1..max_tasks,
    [ 1, 2, 3,     % Job 0 tasks: machines 1,2,3
      1, 3, 2,     % Job 1 tasks: machines 1,3,2
      2, 3, 1      % Job 2 tasks: machines 2,3,(dummy)
    ]);

array[1..n_jobs, 1..max_tasks] of int: duration =
  array2d(1..n_jobs, 1..max_tasks,
    [ 3, 2, 2,     % Job 0 durations
      2, 1, 4,     % Job 1 durations
      4, 3, 0      % Job 2 durations (last is dummy)
    ]);

% Compute an upper bound on the schedule horizon
int: horizon = sum([ duration[j,t] | j in 1..n_jobs, t in 1..max_tasks ]);

% Decision variables: start times for each task
array[1..n_jobs, 1..max_tasks] of var 0..horizon: start;

% Makespan variable
var 0..horizon: makespan;

% 1) Precedence constraints within each job
constraint
  forall(j in 1..n_jobs, t in 1..num_tasks[j]-1) (
    start[j,t] + duration[j,t] <= start[j,t+1]
  );

% 2) Machine capacity constraints: no overlap on the same machine
constraint
  forall(m in 1..n_machines) (
    let {
      array[int] of var int: S = [ start[j,t] 
        | j in 1..n_jobs, t in 1..max_tasks 
        where t <= num_tasks[j] /\ machine[j,t] == m ],
      array[int] of int: D = [ duration[j,t] 
        | j in 1..n_jobs, t in 1..max_tasks
        where t <= num_tasks[j] /\ machine[j,t] == m ],
      array[int] of int: H = [1 | j in 1..n_jobs, t in 1..max_tasks
        where t <= num_tasks[j] /\ machine[j,t] == m ]
    } in
      cumulative(S, D, H, 1)
  );

% 3) Define makespan as the completion time of the last task
constraint
  forall(j in 1..n_jobs, t in 1..num_tasks[j]) (
    makespan >= start[j,t] + duration[j,t]
  );

% Objective: minimize the makespan
solve minimize makespan;

% Output the optimal makespan in JSON format
output [
  "{",
  join(",", [
    "\"" ++ "makespan" ++ "\": " ++ show(makespan)
  ]),
  "}"
];
