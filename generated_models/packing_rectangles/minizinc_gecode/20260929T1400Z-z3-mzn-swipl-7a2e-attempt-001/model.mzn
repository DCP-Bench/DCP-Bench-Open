% Rectangle packing: place rectangles of given widths and heights, without
% overlap and without rotation, inside the smallest possible enclosing rectangle
% (smallest area). Positions start at 0.
include "globals.mzn";

array[int] of int: widths;
array[int] of int: heights;
set of int: Items = index_set(widths);

% The enclosing rectangle is at least as wide / high as the widest / tallest
% item and never needs to exceed placing all items side by side / on top of each other.
var max(widths)..sum(widths): total_x;
var max(heights)..sum(heights): total_y;

% pos_x[i], pos_y[i] = lower-left corner of item i
array[Items] of var 0..sum(widths): pos_x;
array[Items] of var 0..sum(heights): pos_y;

% every item lies completely inside the enclosing rectangle
constraint forall(i in Items) (pos_x[i] + widths[i] <= total_x /\ pos_y[i] + heights[i] <= total_y);

% no two items overlap
constraint diffn(pos_x, pos_y, widths, heights);

% minimise the area of the enclosing rectangle
var int: objective = total_x * total_y;
solve minimize objective;

output ["{\"pos_x\": [", join(", ", [show(pos_x[i]) | i in Items]),
        "], \"pos_y\": [", join(", ", [show(pos_y[i]) | i in Items]),
        "], \"total_x\": ", show(total_x), ", \"total_y\": ", show(total_y), "}"];
