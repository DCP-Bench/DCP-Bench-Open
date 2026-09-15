include "globals.mzn";

array[int] of int: a;
array[int] of int: c;
array[int] of int: u;
int: b;

set of int: Products = index_set(a);
array[Products] of var 0..max(u): x;

% The reference clears the divisions by scaling with the least common multiple
% of a. The product of a is also a common multiple, and scales both sides of the
% same inequality, so the constraint is the one the reference states.
int: scale = product(j in Products) (a[j]);
constraint sum(j in Products) ((scale div a[j]) * x[j]) <= b * scale;
constraint forall(j in Products) (x[j] <= u[j]);

var int: objective = sum(j in Products) (c[j] * x[j]);
solve maximize objective;

output ["{\"x\": [", join(", ", [show(x[j]) | j in Products]),
        "], \"total_profit\": ", show(objective), "}"];
