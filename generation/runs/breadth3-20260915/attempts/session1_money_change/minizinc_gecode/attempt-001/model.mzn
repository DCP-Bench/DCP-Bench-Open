include "globals.mzn";

int: amount;
array[int] of int: types_of_coins;
array[int] of int: available_coins;

set of int: Kinds = index_set(types_of_coins);
array[Kinds] of var 0..max(available_coins): coin_counts;

constraint sum(i in Kinds) (coin_counts[i] * types_of_coins[i]) = amount;
constraint forall(i in Kinds) (coin_counts[i] <= available_coins[i]);

var int: objective = sum(i in Kinds) (coin_counts[i]);
solve minimize objective;

output ["{\"coin_counts\": [", join(", ", [show(coin_counts[i]) | i in Kinds]), "]}"];
