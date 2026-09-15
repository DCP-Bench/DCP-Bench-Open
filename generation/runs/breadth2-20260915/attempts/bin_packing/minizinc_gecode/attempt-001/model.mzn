include "globals.mzn";

array[int] of int: weights;
int: capacity;
int: num_bins;

set of int: Items = index_set(weights);
array[Items] of var 0..num_bins-1: bins;

% The reference writes this for every index of weights; beyond num_bins no item
% can be in that bin and the constraint is vacuous.
constraint forall(i in Items) (
    sum(j in Items) (weights[j] * bool2int(bins[j] = i)) <= capacity);

solve satisfy;

output ["{\"bins\": [", join(", ", [show(bins[j]) | j in Items]), "]}"];
