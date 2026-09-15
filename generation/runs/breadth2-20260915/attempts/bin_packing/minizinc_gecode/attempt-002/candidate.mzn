include "globals.mzn";

array[int] of int: weights;
int: capacity;
int: num_bins;

set of int: Items = index_set(weights);
array[Items] of var 0..num_bins-1: bins;

% The reference writes this for i in range(len(weights)) with 0-based bin
% indices; beyond num_bins no item can be in that bin and it is vacuous.
constraint forall(i in 0..length(weights)-1) (
    sum(j in Items) (weights[j] * bool2int(bins[j] = i)) <= capacity);

solve satisfy;

output ["{\"bins\": [", join(", ", [show(bins[j]) | j in Items]), "]}"];
