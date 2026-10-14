% Covering (OPL example covering.mod): hire a set of workers so that every task
% has at least one qualified worker, at the least total hiring cost.
include "globals.mzn";

int: nb_workers;                          % number of workers
int: num_tasks;                           % number of tasks
array[int] of int: Cost;                  % hiring cost of each worker
% Qualified[j] lists the (1-based) workers qualified for task j. The rows differ
% in length, so the runner pads them with 0; only the first Qualified_len[j]
% entries of row j are real workers.
array[int,int] of int: Qualified;
array[int] of int: Qualified_len;

set of int: Workers = 1..nb_workers;
set of int: Tasks = 1..num_tasks;

% workers[i] = true if worker i is hired
array[Workers] of var bool: workers;

% total cost of the hired workers
var 0..nb_workers*sum(Cost): total_cost = sum(i in Workers) (Cost[i] * bool2int(workers[i]));

% every task is performed: at least one worker qualified for it is hired
constraint forall(j in Tasks) (
    exists(k in 1..Qualified_len[j]) (workers[Qualified[j, k]]));

% minimise the total hiring cost
var int: objective = total_cost;
solve minimize objective;

output ["{\"total_cost\": ", show(total_cost),
        ", \"workers\": [", join(", ", [show(workers[i]) | i in Workers]), "]}"];
