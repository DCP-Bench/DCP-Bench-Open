% Autoref: find a series s[0..n+1] in which every i from 0 to n occurs exactly
% s[i] times, and whose last element s[n+1] equals m.
include "globals.mzn";

int: n;
int: m;  % required value of the last element

% the series has n + 2 positions; every value lies between 0 and n
array[0..n+1] of var 0..n: s;

% the last element is m
constraint s[n + 1] = m;

% the value i occurs exactly s[i] times in the series
constraint forall(i in 0..n) (count(s, i) = s[i]);

solve satisfy;

output ["{\"s\": [", join(", ", [show(s[k]) | k in 0..n+1]), "]}"];
