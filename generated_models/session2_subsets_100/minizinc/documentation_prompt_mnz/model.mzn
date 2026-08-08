include "globals.mzn";

% Given set A of 10 distinct integers
array[1..10] of int: A = [81, 21, 79, 4, 29, 70, 28, 20, 14, 7];

% Decision variables: binary indicators for membership in subsets S and T
array[1..10] of var 0..1: in_S;
array[1..10] of var 0..1: in_T;

% Constraints:

% 1) S and T are disjoint subsets: no element can be in both
constraint forall(i in 1..10) (
    in_S[i] + in_T[i] <= 1
);

% 2) Both subsets are non-empty
constraint sum(i in 1..10)(in_S[i]) >= 1;
constraint sum(i in 1..10)(in_T[i]) >= 1;

% 3) The sums of elements in S and T are equal
constraint sum(i in 1..10)(in_S[i] * A[i]) = sum(i in 1..10)(in_T[i] * A[i]);

solve satisfy;

output [
    "{",
    "\"in_S\": ", show(in_S), ",",
    "\"in_T\": ", show(in_T),
    "}"
];