include "globals.mzn";

array[int] of int: values;
array[int] of int: weights;
int: capacity;

set of int: Items = index_set(values);
array[Items] of var bool: x;

constraint sum(i in Items) (weights[i] * bool2int(x[i])) <= capacity;

var int: objective = sum(i in Items) (values[i] * bool2int(x[i]));
solve maximize objective;

output ["{\"x\": [", join(", ", [show(x[i]) | i in Items]), "]}"];
