# Plan: packing_rectangles (gecode_cpp, attempt-001)

- place each rectangle inside the bounding rectangle, with its left and bottom edges at pos_x[i], pos_y[i] (no rotation; the description does not allow one) -> rel(*this, pos_x[i] + w[i] <= total_x); rel(*this, pos_y[i] + h[i] <= total_y)  [linear; the box must contain every item]
- no two rectangles overlap -> nooverlap(*this, pos_x, IntArgs(w), pos_y, IntArgs(h))  [the rectangle-packing global, from the skill's constraint map]
- bounds of the bounding rectangle: total_x in [max width, sum of widths], total_y in [max height, sum of heights]; a compacted packing has every edge within the sum of widths (heights) -> domain of total_x, total_y and pos_x, pos_y  [derived, valid for any optimum]
- the bounding rectangle holds all items, so its area is at least the sum of the item areas -> rel(*this, area >= sum_area)  [redundant implied bound from the instance data]
- objective: minimise the total area -> area = expr(*this, total_x * total_y); minimize(area)
- branching: total_x and total_y first (they fix the box, which bounds all positions), then pos_x and pos_y by first-fail, smallest value first (INT_VAR_SIZE_MIN, INT_VAL_MIN)
- redundant on each axis: the rectangles crossing a vertical line have heights summing to at most total_y -> cumulative(*this, total_y, pos_x, IntArgs(w), IntArgs(h)); same for y with total_x  [skill: a cumulative beside nooverlap pays; cut the 8-square instance from timeout (60 s) to 2 ms in the quick check]
