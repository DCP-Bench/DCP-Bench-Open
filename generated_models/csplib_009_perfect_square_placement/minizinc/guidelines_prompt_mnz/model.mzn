
% Include standard library
include "globals.mzn";

% Input data
int: base = 6;                        % Side length of the large square
array[1..9] of int: sides = [3,3,3,2,1,1,1,1,1];  % Side lengths of the smaller squares
int: n = length(sides);               % Number of small squares

% Decision variables: lower-left corner (x, y) for each square
array[1..n] of var 0..base: x_coords;
array[1..n] of var 0..base: y_coords;

% Each square must lie entirely within the big square
constraint
  forall(i in 1..n) (
    x_coords[i] + sides[i] <= base /\
    y_coords[i] + sides[i] <= base
  );

% No overlapping: for each pair, one is to the left, right, above or below the other
constraint
  forall(i, j in 1..n where i < j) (
    x_coords[i] + sides[i] <= x_coords[j]
    \/ x_coords[j] + sides[j] <= x_coords[i]
    \/ y_coords[i] + sides[i] <= y_coords[j]
    \/ y_coords[j] + sides[j] <= y_coords[i]
  );

solve satisfy;

% Output in JSON format
output [
  "{",
    "\"x_coords\": [" ++ join(",", [ show(x_coords[i]) | i in 1..n ]) ++ "],",
    "\"y_coords\": [" ++ join(",", [ show(y_coords[i]) | i in 1..n ]) ++ "]",
  "}"
];
