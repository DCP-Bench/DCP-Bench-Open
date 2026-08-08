include "globals.mzn";

% Input data
int: n = 4;
array[1..n] of int: widths = [3, 4, 2, 1];
array[1..n] of int: heights = [2, 3, 1, 4];

% Upper bounds for the container dimensions (sum of widths and heights)
int: max_width = sum(widths);
int: max_height = sum(heights);

% Decision variables: positions of each item (bottom-left corner)
array[1..n] of var 0..max_width: pos_x;
array[1..n] of var 0..max_height: pos_y;

% Dimensions of the larger rectangle to be minimized
var 0..max_width: total_x;
var 0..max_height: total_y;

% Constraints to ensure all items are within the larger rectangle boundaries
constraint forall(i in 1..n) (
    pos_x[i] + widths[i] <= total_x /\
    pos_y[i] + heights[i] <= total_y
);

% Non-overlapping constraints for all pairs of items
constraint forall(i, j in 1..n where i < j) (
    (pos_x[i] + widths[i] <= pos_x[j]) \/
    (pos_x[j] + widths[j] <= pos_x[i]) \/
    (pos_y[i] + heights[i] <= pos_y[j]) \/
    (pos_y[j] + heights[j] <= pos_y[i])
);

% Objective: minimize the total area of the larger rectangle
var int: total_area = total_x * total_y;
solve minimize total_area;

output [
    "{",
    "\"pos_x\": ", show(pos_x), ",",
    "\"pos_y\": ", show(pos_y), ",",
    "\"total_x\": ", show(total_x), ",",
    "\"total_y\": ", show(total_y),
    "}"
];