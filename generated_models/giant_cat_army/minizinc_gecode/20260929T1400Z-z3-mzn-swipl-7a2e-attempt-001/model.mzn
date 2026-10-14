% Giant cat army riddle: start from [0] and extend the list by adding 5, adding
% 7 or taking a square root, so that all numbers are different integers of at
% most 60, the list contains 2, then 10, then 14 (in that order), and it ends
% with 14 after exactly 24 numbers.
include "globals.mzn";

% The riddle fixes these numbers, so they are mirrored here.
int: max_value = 60;  % largest number allowed in the list
int: length = 24;     % number of entries in the list
int: goal = 14;       % the last entry

% x[i] = the i-th number of the list
array[1..length] of var 0..max_value: x;

% all numbers are different
constraint all_different(x);

% the list starts with 0 and ends with 14
constraint x[1] = 0;
constraint x[length] = goal;

% each number follows the previous one by adding 5, adding 7, or taking the
% square root (the previous number x[i] is the square of the next x[i+1])
constraint forall(i in 1..length - 1) (x[i + 1] = x[i] + 5 \/ x[i + 1] = x[i] + 7 \/ x[i] = x[i + 1] * x[i + 1]);

% the list contains 2 and later 10 (and, as it ends with it, 14 after both)
constraint exists(i in 2..length, j in 3..length where i < j) (x[i] = 2 /\ x[j] = 10);

solve satisfy;

output ["{\"x\": [", join(", ", [show(x[i]) | i in 1..length]), "]}"];
