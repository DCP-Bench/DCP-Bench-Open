include "globals.mzn";

int: total_coins_lost;
array[int] of int: coin_numbers;

set of int: Kinds = index_set(coin_numbers);
array[Kinds] of var 0..total_coins_lost: bags;

constraint sum(i in Kinds) (coin_numbers[i] * bags[i]) = total_coins_lost;

solve satisfy;

output ["{\"bags\": [", join(", ", [show(bags[i]) | i in Kinds]), "]}"];
