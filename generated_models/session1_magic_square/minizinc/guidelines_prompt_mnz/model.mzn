
% Magic Square of size 4
include "globals.mzn";

int: n = 4;
int: target = n * (n*n + 1) div 2;  % Magic constant: 34 for n=4

% Decision variables: a 4x4 matrix with values 1..16
array[1..n, 1..n] of var 1..n*n: square;

% All cells must be distinct
constraint
    all_different([ square[i,j] | i,j in 1..n ]);

% Row sums and column sums must equal target
constraint
    forall(i in 1..n) (
        sum(j in 1..n)( square[i,j] ) == target
    ) /\
    forall(j in 1..n) (
        sum(i in 1..n)( square[i,j] ) == target
    );

% Both main diagonals must sum to target
constraint
    sum(i in 1..n)( square[i,i] ) == target /\
    sum(i in 1..n)( square[i, n+1-i] ) == target;

solve satisfy;

% Output the solution in JSON: "square" : list of lists
output [
    "{"
    ++ "\"square\": "
    ++ "["
    ++ join(",", [ "[" ++ join(",", [ show(square[i,j]) | j in 1..n ]) ++ "]"
                  | i in 1..n ])
    ++ "]"
    ++ "}"
];
