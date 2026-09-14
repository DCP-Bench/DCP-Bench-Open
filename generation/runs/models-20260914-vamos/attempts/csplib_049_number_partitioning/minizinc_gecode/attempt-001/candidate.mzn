include "globals.mzn";

int: n;
int: half = n div 2;

array[1..half] of var 1..n: x;
array[1..half] of var 1..n: y;

constraint all_different(x ++ y);
constraint sum(x) = sum(y);
constraint sum(i in 1..half) (x[i] * x[i]) = sum(i in 1..half) (y[i] * y[i]);

solve satisfy;

output ["{\"A\": [", join(", ", [show(x[i]) | i in 1..half]),
        "], \"B\": [", join(", ", [show(y[i]) | i in 1..half]), "]}"];
