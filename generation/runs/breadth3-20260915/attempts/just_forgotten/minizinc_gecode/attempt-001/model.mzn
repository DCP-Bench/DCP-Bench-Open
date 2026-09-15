include "globals.mzn";

array[int, int] of int: sets;
int: num_correct_digits;

set of int: Guesses = index_set_1of2(sets);
set of int: Positions = index_set_2of2(sets);
int: n = card(Positions);
array[Positions] of var 0..n-1: x;

constraint all_different(x);
constraint forall(g in Guesses) (
    sum(i in Positions) (bool2int(x[i] = sets[g, i])) = num_correct_digits);

solve satisfy;

output ["{\"x\": [", join(", ", [show(x[i]) | i in Positions]), "]}"];
