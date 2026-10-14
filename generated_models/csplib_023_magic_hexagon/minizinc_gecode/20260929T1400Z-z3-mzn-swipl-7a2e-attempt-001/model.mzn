% Magic hexagon: place the numbers 1..19 in the 19 cells of a hexagon (rows of
% 3, 4, 5, 4, 3 cells) so that the numbers along each of the 15 lines add up to
% the same magic sum.
include "globals.mzn";

int: NUM_CELLS;
int: MAGIC_SUM;

% The geometry is fixed by the problem. Cells are numbered row by row from 1:
%       1  2  3
%     4  5  6  7
%   8  9 10 11 12
%    13 14 15 16
%      17 18 19
array[1..15] of set of int: lines = [
    % the 5 horizontal rows
    {1, 2, 3}, {4, 5, 6, 7}, {8, 9, 10, 11, 12}, {13, 14, 15, 16}, {17, 18, 19},
    % the 5 diagonals running from top left to bottom right
    {1, 4, 8}, {2, 5, 9, 13}, {3, 6, 10, 14, 17}, {7, 11, 15, 18}, {12, 16, 19},
    % the 5 diagonals running from top right to bottom left
    {3, 7, 12}, {2, 6, 11, 16}, {1, 5, 10, 15, 19}, {4, 9, 14, 18}, {8, 13, 17}];

% LD[c] = the number in cell c
array[1..NUM_CELLS] of var 1..NUM_CELLS: LD;

% every number from 1 to 19 is used exactly once
constraint all_different(LD);

% every line of the hexagon adds up to the magic sum
constraint forall(l in 1..15) (sum(c in lines[l]) (LD[c]) = MAGIC_SUM);

solve satisfy;

output ["{\"LD\": [", join(", ", [show(LD[c]) | c in 1..NUM_CELLS]), "]}"];
