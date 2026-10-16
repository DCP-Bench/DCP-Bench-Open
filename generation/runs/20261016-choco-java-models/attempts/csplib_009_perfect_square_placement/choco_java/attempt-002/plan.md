# Plan: perfect square placement (csplib_009), attempt 2

- pack squares with the given sides into a big square -> one square per side at (x_i, y_i), domains 0..base-side_i
- squares do not overlap -> m.diffN(x, y, w, h, true)
- borders parallel to the big square -> axis-aligned, same x and y as above
- sum of square surfaces equals the packing surface (no spare capacity) -> checked on the data, sum(side_i^2) == base^2
- redundant: along the x axis, at every column the squares crossing it cover at most base units -> m.cumulative(x, sides, sides, base)
- redundant: along the y axis, at every row the squares crossing it cover at most base units -> m.cumulative(y, sides, sides, base)
- coordinates start from 0 -> domains start at 0
- output x_coords, y_coords
- objective: none (satisfaction)
- search: dom/wdeg on all coordinates with Luby restarts (attempt 1 timed out on the 21-square instance)
