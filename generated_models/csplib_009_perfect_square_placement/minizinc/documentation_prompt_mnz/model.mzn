include "globals.mzn";

% Input data
int: base = 6;  % Side length of the large square
array[1..9] of int: sides = [3, 3, 3, 2, 1, 1, 1, 1, 1];  % Side lengths of the smaller squares
int: n = length(sides);

% Decision variables: coordinates of the bottom-left corner of each small square
array[1..n] of var 0..base: x_coords;
array[1..n] of var 0..base: y_coords;

% Constraints

% Each square must be fully inside the big square
constraint
  forall(i in 1..n) (
    x_coords[i] + sides[i] <= base /\
    y_coords[i] + sides[i] <= base
  );

% No overlapping squares
constraint
  forall(i, j in 1..n where i < j) (
    (x_coords[i] + sides[i] <= x_coords[j]) \/
    (x_coords[j] + sides[j] <= x_coords[i]) \/
    (y_coords[i] + sides[i] <= y_coords[j]) \/
    (y_coords[j] + sides[j] <= y_coords[i])
  );

solve satisfy;

output [
  "{",
  "\"x_coords\": ", show(x_coords), ",",
  "\"y_coords\": ", show(y_coords),
  "}"
];