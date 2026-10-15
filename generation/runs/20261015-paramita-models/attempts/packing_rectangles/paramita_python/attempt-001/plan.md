Place rectangles i (widths w[i], heights h[i]) with no overlap, all inside the box total_x by total_y -> pos_x[i] and pos_y[i] unary order bits (domain 0..SX-1, SX = sum of widths), total_x and total_y unary bits gx, gy (domain 1..SX / 1..SY); box bound: pos_x[i] + w[i] <= total_x as PB over unit-coefficient bits, same for y.
No overlap per pair (i, j) -> four reified Bools (i left of j, j left of i, i below j, j below i), Or of the four, each If(sep, PB inequality over the position sums).
Box is at least as wide as the widest item -> gx unit bits for a <= max(w), same for y (implied by placement).
Objective: minimise the area total_x * total_y -> product of two unary numbers: cell Bool c[a][b] with If(gx[a] & gy[b], c[a][b]) and unit weight; the sum of cells equals total_x * total_y.
Output pos_x, pos_y as integer expressions (sum of their unary bits), total_x and total_y as sums of their bits; objective is the area.
