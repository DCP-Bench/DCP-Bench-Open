% Sudoku: complete a 9 x 9 grid so that every row, column and 3 x 3 box holds
% each of the digits 1..9 once, keeping the digits already given.
cell(0..8).
digit(1..9).

% Every cell holds exactly one digit.
1 { grid(R,C,V) : digit(V) } 1 :- cell(R), cell(C).

% The given digits stay (0 marks an empty cell).
:- input_grid(R,C,V), V != 0, not grid(R,C,V).

% No digit repeats in a row, in a column, or in a 3 x 3 box.
:- grid(R,C1,V), grid(R,C2,V), C1 < C2.
:- grid(R1,C,V), grid(R2,C,V), R1 < R2.
:- grid(R1,C1,V), grid(R2,C2,V), (R1,C1) < (R2,C2), R1 / 3 == R2 / 3, C1 / 3 == C2 / 3.

#show grid/3.
