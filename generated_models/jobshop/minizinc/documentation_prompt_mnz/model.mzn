include "globals.mzn";

% Input data: jobs_data[job][task] = (machine, duration)
array[int, int] of int: machines = [
    | 0, 1, 2
    | 0, 2, 1
    | 1, 2, 0  % padding for job 2 to have same length, will ignore last
];
array[int, int] of int: durations = [
    | 3, 2, 2
    | 2, 1, 4
    | 4, 3, 0  % padding for job 2
];

int: num_jobs = 3;
int: max_tasks = 3; % max number of tasks per job (padded)
int: num_machines = 3;

% Compute actual number of tasks per job
array[1..num_jobs] of int: tasks_per_job = [3, 3, 2];

% Decision variables: start times of each task
array[1..num_jobs, 1..max_tasks] of var 0..100: start_times;

% Compute end times of each task
array[1..num_jobs, 1..max_tasks] of var 0..100: end_times;
constraint
    forall(j in 1..num_jobs, t in 1..max_tasks) (
        end_times[j,t] = start_times[j,t] + durations[j,t]
    );

% Precedence constraints: tasks in a job must be done in order
constraint
    forall(j in 1..num_jobs, t in 1..max_tasks-1 where t < tasks_per_job[j]) (
        end_times[j,t] <= start_times[j,t+1]
    );

% Collect all tasks per machine for disjunctive constraints
% For each machine, collect the tasks assigned to it
array[1..num_machines] of var int: dummy; % dummy to use array comprehension

% We create arrays of tasks per machine
% We store the start times and durations of tasks on each machine
array[1..num_machines] of array[int] of var int: machine_task_starts;
array[1..num_machines] of array[int] of int: machine_task_durations;

% We need to build these arrays dynamically
% First, count number of tasks per machine
array[1..num_machines] of int: machine_task_counts = [
    sum([bool2int(machines[j,t] == m) | j in 1..num_jobs, t in 1..tasks_per_job[j]]) | m in 0..num_machines-1
];

% Indexing tasks per machine
array[1..num_machines] of array[int] of int: machine_task_job;
array[1..num_machines] of array[int] of int: machine_task_task;

% Build arrays for each machine
% We use comprehension with let to build arrays
function array[int] of var int: get_machine_task_starts(int: m) =
    [start_times[j,t] | j,t in 1..num_jobs, 1..tasks_per_job[j] where machines[j,t] == m];

function array[int] of int: get_machine_task_durations(int: m) =
    [durations[j,t] | j,t in 1..num_jobs, 1..tasks_per_job[j] where machines[j,t] == m];

% For disjunctive constraints, we use no-overlap on tasks per machine
constraint
    forall(m in 0..num_machines-1) (
        let {
            array[int] of var int: s = get_machine_task_starts(m),
            array[int] of int: d = get_machine_task_durations(m)
        } in
        disjunctive(s, d)
    );

% Makespan: maximum of all end times of last tasks of each job
var 0..100: makespan;
constraint
    makespan = max([end_times[j, tasks_per_job[j]] | j in 1..num_jobs]);

solve minimize makespan;

output [
    "{",
    "\"makespan\": ", show(makespan),
    "}"
];