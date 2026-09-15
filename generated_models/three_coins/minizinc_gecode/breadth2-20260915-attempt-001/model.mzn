include "globals.mzn";

int: num_moves;
array[int] of int: init;

set of int: Coins = index_set(init);
array[0..num_moves, Coins] of var bool: x;

constraint forall(j in Coins) (x[0, j] = (init[j] = 1));
constraint forall(m in 1..num_moves) (
    sum(j in Coins) (bool2int(x[m, j] != x[m - 1, j])) = 1);
% The last row is all heads or all tails.
constraint let { var int: last = sum(j in Coins) (bool2int(x[num_moves, j])) } in
    last = 0 \/ last = length(init);

solve satisfy;

output ["{\"steps\": [",
        join(", ", ["[" ++ join(", ", [show(x[m, j]) | j in Coins]) ++ "]" | m in 0..num_moves]),
        "]}"];
