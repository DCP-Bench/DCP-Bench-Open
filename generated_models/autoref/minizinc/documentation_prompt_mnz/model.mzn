include "globals.mzn";

% Input data
int: n = 27;
int: m = 5;

% The series S has length n+2 (indices 0..n+1)
% s[i] = number of occurrences of i in S for i in 0..n
% s[n+1] = m (given)
array[0..n+1] of var 0..sum(0..n)(i) + m: s;

% Constraint 1: For each i in 0..n, s[i] equals the number of occurrences of i in S
% The series S is s itself, so the count of i in s equals s[i]
% Constraint 2: s[n+1] = m
constraint s[n+1] = m;

% The series S is s, so count occurrences of i in s equals s[i]
constraint forall(i in 0..n) (
    count(s, i) == s[i]
);

% The series S must be non-empty
constraint sum(i in 0..n+1)(s[i]) > 0;

solve satisfy;

output [
    "{",
    "\"s\": ", show(s),
    "}"
];