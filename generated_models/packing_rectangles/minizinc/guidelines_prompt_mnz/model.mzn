
include "globals.mzn";

% Input data
int: n = 4;
array[1..n] of int: widths  = [3, 4, 2, 1];
array[1..n] of int: heights = [2, 3, 1, 4];

% Upper bounds for the container dimensions
int: ubW = sum(widths);
int: ubH = sum(heights);

% Decision variables: positions of each rectangle
array[1..n] of var 0..ubW: pos_x;
array[1..n] of var 0..ubH: pos_y;

% Decision variables: total width and height of the enclosing rectangle
var 0..ubW: total_x;
var 0..ubH: total_y;

% Define the area to minimize
var int: area = total_x * total_y;

% Ensure each rectangle lies within the container
constraint
  forall(i in 1..n) (
    pos_x[i] + widths[i]  <= total_x /\
    pos_y[i] + heights[i] <= total_y
  );

% Non-overlap constraint using global diffn
constraint
  diffn(pos_x, pos_y, widths, heights);

solve minimize area;

output [
  "{",
    "\"pos_x\": [" ++ join(",", [ show(pos_x[i])  | i in 1..n ]) ++ "],",
    "\"pos_y\": [" ++ join(",", [ show(pos_y[i])  | i in 1..n ]) ++ "],",
    "\"total_x\": " ++ show(total_x) ++ ",",
    "\"total_y\": " ++ show(total_y),
  "}"
];
