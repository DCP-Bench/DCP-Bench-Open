include "globals.mzn";

array[int] of int: isbn_init;

set of int: Digits = index_set(isbn_init);
int: n = length(isbn_init);
array[Digits] of var 0..9: isbn;

% A -1 in the instance marks the digit to find.
constraint forall(i in Digits where isbn_init[i] != -1) (isbn[i] = isbn_init[i]);
constraint isbn[1] = 9;
constraint isbn[2] = 7;
constraint isbn[3] = 8 \/ isbn[3] = 9;
constraint isbn[n] = (10 - (sum(i in 1..n-1) (isbn[i] * (if i mod 2 = 1 then 1 else 3 endif)) mod 10)) mod 10;

solve satisfy;

output ["{\"isbn\": [", join(", ", [show(isbn[i]) | i in Digits]), "]}"];
