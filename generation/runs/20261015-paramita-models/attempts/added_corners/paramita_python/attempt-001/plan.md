Enter the digits 1 through 8 in the circles and squares -> one-hot value per cell: exactly one of x_p_1..x_p_8 per cell p (reading order 0..7), exactly one value per cell
such that ... each digit used once -> per value v: sum over the 8 cells of x_p_v == 1 (permutation)
the number in each square is equal to the sum of the numbers in the adjoining circles -> per square s with adjoining circles c1, c2: val[s] == val[c1] + val[c2] (PB over integer expressions)
figure C F C / F _ F / C F C: C = circle (corners), F = square (edge midpoints), each square adjoins the two circles next to it in the figure
print positions in reading order (left to right, top to bottom) -> outputs positions = list of the 8 cell values
objective -> none (satisfaction)
