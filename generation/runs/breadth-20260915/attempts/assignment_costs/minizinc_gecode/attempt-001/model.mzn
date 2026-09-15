include "globals.mzn";

array[int, int] of int: cost;

set of int: Tasks = index_set_1of2(cost);
set of int: People = index_set_2of2(cost);
array[Tasks, People] of var bool: x;

constraint forall(i in Tasks) (sum(j in People) (bool2int(x[i, j])) = 1);
constraint forall(j in People) (sum(i in Tasks) (bool2int(x[i, j])) <= 1);

var int: objective = sum(i in Tasks, j in People) (cost[i, j] * bool2int(x[i, j]));
solve minimize objective;

output ["{\"x\": [",
        join(", ", ["[" ++ join(", ", [show(x[i, j]) | j in People]) ++ "]" | i in Tasks]),
        "]}"];
