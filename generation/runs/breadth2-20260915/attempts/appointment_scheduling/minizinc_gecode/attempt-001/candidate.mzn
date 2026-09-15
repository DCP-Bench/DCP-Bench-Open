include "globals.mzn";

array[int, int] of int: m;

set of int: People = index_set_1of2(m);
set of int: Slots = index_set_2of2(m);
array[People, Slots] of var bool: x;

constraint forall(i in People) (
    sum(j in Slots) (m[i, j] * bool2int(x[i, j])) = 1
 /\ sum(j in Slots) (bool2int(x[i, j])) = 1
 /\ sum(j in People) (bool2int(x[j, i])) = 1);

solve satisfy;

output ["{\"x\": [",
        join(", ", ["[" ++ join(", ", [show(x[i, j]) | j in Slots]) ++ "]" | i in People]),
        "]}"];
