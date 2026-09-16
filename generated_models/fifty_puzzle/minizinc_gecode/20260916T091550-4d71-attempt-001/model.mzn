% Fifty puzzle: knock over a set of dummies whose numbers total exactly the
% target sum.
include "globals.mzn";

array[int] of int: values;
int: target_sum;

set of int: Dummies = index_set(values);
array[Dummies] of var bool: dummies;

constraint sum(i in Dummies) (values[i] * bool2int(dummies[i])) = target_sum;

solve satisfy;

output ["{\"dummies\": [", join(", ", [show(dummies[i]) | i in Dummies]), "]}"];
