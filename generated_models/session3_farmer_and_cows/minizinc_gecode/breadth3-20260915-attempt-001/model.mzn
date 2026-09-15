include "globals.mzn";

int: num_cows;
int: num_sons;
array[int] of int: cows_per_son;

set of int: Cows = 1..num_cows;
set of int: Sons = 0..num_sons-1;
% The reference's own derived data: cow i produces i units of milk.
array[Cows] of int: milk = [i | i in Cows];
int: share = sum(milk) div num_sons;

array[Cows] of var Sons: cow_assignments;

constraint forall(s in Sons) (
    sum(i in Cows) (bool2int(cow_assignments[i] = s)) = cows_per_son[s + 1]
 /\ sum(i in Cows) (milk[i] * bool2int(cow_assignments[i] = s)) = share);

solve satisfy;

output ["{\"cow_assignments\": [", join(", ", [show(cow_assignments[i]) | i in Cows]), "]}"];
