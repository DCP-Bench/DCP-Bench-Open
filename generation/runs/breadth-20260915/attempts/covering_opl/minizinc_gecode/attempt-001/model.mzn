include "globals.mzn";

int: nb_workers;
int: num_tasks;
array[int] of array[int] of int: Qualified;
array[int] of int: Cost;

set of int: Workers = 1..nb_workers;
array[Workers] of var bool: workers;
var 0..nb_workers * sum(Cost): total_cost;

constraint total_cost = sum(i in Workers) (Cost[i] * bool2int(workers[i]));
% Qualified lists its workers 1-based.
constraint forall(t in 1..num_tasks) (
    sum(w in index_set(Qualified[t])) (bool2int(workers[Qualified[t][w]])) >= 1);

var int: objective = total_cost;
solve minimize objective;

output ["{\"total_cost\": ", show(total_cost),
        ", \"workers\": [", join(", ", [show(workers[i]) | i in Workers]), "]}"];
