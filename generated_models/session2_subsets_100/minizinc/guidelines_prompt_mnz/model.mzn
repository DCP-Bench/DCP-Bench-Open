
% Include necessary global constraints library
include "globals.mzn";

% Input data
int: n = 10;
array[1..n] of int: A = [81,21,79,4,29,70,28,20,14,7];

% Decision variables: binary indicators for membership in S and T
array[1..n] of var 0..1: in_S;
array[1..n] of var 0..1: in_T;

% Constraints
% 1) S and T are disjoint
constraint forall(i in 1..n)(in_S[i] + in_T[i] <= 1);

% 2) Non-empty subsets
constraint sum(i in 1..n)(in_S[i]) >= 1;
constraint sum(i in 1..n)(in_T[i]) >= 1;

% 3) Equal sums of elements in S and T
constraint sum(i in 1..n)(in_S[i] * A[i]) = sum(i in 1..n)(in_T[i] * A[i]);

% Solve the satisfaction problem
solve satisfy;

% Output solution in JSON format
output [
    "{",
    "\"in_S\": [" ++ join(",", [show(in_S[i]) | i in 1..n]) ++ "],",
    "\"in_T\": [" ++ join(",", [show(in_T[i]) | i in 1..n]) ++ "]",
    "}"
];
