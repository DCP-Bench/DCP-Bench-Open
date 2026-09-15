include "globals.mzn";

array[int] of int: ratings;

set of int: Children = index_set(ratings);
int: n = length(ratings);
array[Children] of var 1..n: x;
var 1..n*n: z;

constraint z = sum(i in Children) (x[i]);
constraint z >= n;
constraint forall(i in Children where i > min(Children)) (
    if ratings[i - 1] > ratings[i] then x[i - 1] > x[i]
    elseif ratings[i - 1] < ratings[i] then x[i - 1] < x[i]
    else true endif);

var int: objective = z;
solve minimize objective;

output ["{\"z\": ", show(z), ", \"x\": [", join(", ", [show(x[i]) | i in Children]), "]}"];
