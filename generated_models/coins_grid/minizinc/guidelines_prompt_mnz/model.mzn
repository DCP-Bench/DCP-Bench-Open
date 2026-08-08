
% Define board size and number of coins per row/column
int: n = 31;
int: k = 14;

% Decision variables: x[i,j] = 1 if there's a coin at row i, column j; 0 otherwise
array[1..n, 1..n] of var 0..1: x;

% Objective variable: sum of squared horizontal distances from main diagonal
var int: z;

% Each row must contain exactly k coins
constraint
  forall(i in 1..n) (
    sum(j in 1..n)( x[i,j] ) = k
  );

% Each column must contain exactly k coins
constraint
  forall(j in 1..n) (
    sum(i in 1..n)( x[i,j] ) = k
  );

% Define the objective: minimize sum_{i,j} x[i,j] * (j - i)^2
constraint
  z = sum(i, j in 1..n)( x[i,j] * (j - i) * (j - i) );

solve minimize z;

output [
  "{",
    "\"x\": [" ++
      join(",", [ 
        "[" ++ join(",", [ show(x[i,j]) | j in 1..n ]) ++ "]"
        | i in 1..n
      ]) ++ "],",
    "\"z\": " ++ show(z),
  "}"
];
