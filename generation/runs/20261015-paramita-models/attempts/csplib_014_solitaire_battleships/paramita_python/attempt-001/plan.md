# Plan: solitaire battleships (csplib_014)

Problem: fill a grid with water, a submarine, or ship parts (left, right, top, bottom, middle) so that the fleet, row sums, column sums and hints hold.

- Each cell: one-hot over the 7 codes read from the instance (WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE). Sum of the 7 Bools == 1.
- Ship-part adjacency (ships not adjacent, even diagonally): each non-water piece forces its 8 neighbours to be water except its own ship neighbours (in-line). L: right in {R,M}; R: left in {L,M}; T: down in {B,M}; B: up in {T,M}; C: all 8 water; M: horizontal (left in {L,M}, right in {R,M}) or vertical (up in {T,M}, down in {B,M}).
- Ship count per length: a horizontal ship of length L starts at L at (r,c), M at c+1..c+L-2, R at c+L-1; aux Bool per start = And of those; sum over starts + vertical starts == fleet count for L. Submarines (length 1) = count of CIRCLE cells.
- Row sums: sum of non-water Bools in row r == rowsum[r]. Column sums likewise.
- Hints: each hint (r,c,code) forces that cell's code.
- Output grid: integer expression code * one-hot bool summed per cell.
- Satisfaction problem, no objective.
