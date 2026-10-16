# packing_rectangles plan

- "placing a set of rectangular items into a larger rectangular area" -> items i with widths[i], heights[i]; container width total_x, height total_y
- "no items overlap" -> m.diffN(pos_x, pos_y, widths, heights, true).post()
- "all items are within the boundaries of the larger area" -> pos_x[i] + widths[i] <= total_x and pos_y[i] + heights[i] <= total_y
- "Print the positions of the items (pos_x, pos_y) starting from 0" -> pos_x, pos_y in 0..bound
- "the dimensions of the larger rectangle (total_x, total_y)" -> total_x, total_y bounded by the sum of widths and heights
- "minimize the total area of the larger rectangle" -> area = total_x * total_y, setObjective MINIMIZE
