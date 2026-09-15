include "globals.mzn";

array[int, int] of int: possible_assignments;

set of int: Participants = index_set_1of2(possible_assignments);
set of int: Cars = index_set_2of2(possible_assignments);
array[Participants, Cars] of var bool: assignments;

constraint forall(i in Participants, j in Cars) (
    bool2int(assignments[i, j]) <= possible_assignments[i, j]);
constraint forall(i in Participants) (sum(j in Cars) (bool2int(assignments[i, j])) <= 1);
constraint forall(j in Cars) (sum(i in Participants) (bool2int(assignments[i, j])) <= 1);

var int: objective = sum(i in Participants, j in Cars) (bool2int(assignments[i, j]));
solve maximize objective;

output ["{\"assignments\": [",
        join(", ", ["[" ++ join(", ", [show(assignments[i, j]) | j in Cars]) ++ "]" | i in Participants]),
        "]}"];
