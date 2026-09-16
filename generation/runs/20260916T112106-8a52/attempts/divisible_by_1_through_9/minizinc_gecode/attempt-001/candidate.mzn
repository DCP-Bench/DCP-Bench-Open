% Divisible by 1 through 9: a ten-digit pandigital number whose first n digits
% form a multiple of n, for every n.
include "globals.mzn";

int: digits = 10;
array[1..digits] of var 0..9: x;
array[1..digits] of var 0..pow(10, digits): t;

constraint all_different(x);
constraint forall(i in 1..digits) (
    t[i] = sum(j in 1..i) (x[j] * pow(10, i - j))
    /\ t[i] mod i = 0
);

solve satisfy;

output ["{\"number\": ", show(t[digits]), "}"];
