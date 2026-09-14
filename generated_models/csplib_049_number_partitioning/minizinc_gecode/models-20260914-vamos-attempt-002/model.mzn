include "globals.mzn";

int: n;
int: half = n div 2;

array[1..half] of var 1..n: x;
array[1..half] of var 1..n: y;

constraint all_different(x ++ y);
constraint sum(x) = sum(y);
constraint sum(i in 1..half) (x[i] * x[i]) = sum(i in 1..half) (y[i] * y[i]);

% Implied: x and y partition 1..n, so each half carries half of the totals.
constraint 4 * sum(x) = n * (n + 1);
constraint 12 * sum(i in 1..half) (x[i] * x[i]) = n * (n + 1) * (2 * n + 1);

solve satisfy;

output ["{\"A\": [", join(", ", [show(x[i]) | i in 1..half]),
        "], \"B\": [", join(", ", [show(y[i]) | i in 1..half]), "]}"];
