include "globals.mzn";

array[int] of int: supply;
array[int] of int: demand;
array[int, int] of int: cost;
array[int, int] of int: limit;

set of int: People = index_set(supply);
set of int: Projects = index_set(demand);
array[People, Projects] of var 0..10: assign;

constraint forall(i in People) (sum(j in Projects) (assign[i, j]) = supply[i]);
constraint forall(j in Projects) (sum(i in People) (assign[i, j]) = demand[j]);
constraint forall(i in People, j in Projects) (assign[i, j] <= limit[i, j]);

var int: objective = sum(i in People, j in Projects) (cost[i, j] * assign[i, j]);
solve minimize objective;

output ["{\"assign\": [",
        join(", ", ["[" ++ join(", ", [show(assign[i, j]) | j in Projects]) ++ "]" | i in People]),
        "], \"total_cost\": ", show(objective), "}"];
