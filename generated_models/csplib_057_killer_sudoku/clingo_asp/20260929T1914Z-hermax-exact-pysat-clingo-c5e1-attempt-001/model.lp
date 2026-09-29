% Killer sudoku: fill a sudoku grid with 1..9 so that each row, column and 3x3
% box holds every digit once, and each cage of cells adds up to its target with
% no digit repeated inside the cage.
% problem(K, 0, Target) is the target sum of cage K and problem(K, 1, J, 0, R),
% problem(K, 1, J, 1, C) the row and column (counted from 1) of its J-th cell.
index(0..N-1) :- n(N).
digit(1..N) :- n(N).

% Every cell holds exactly one digit.
1 { x(R,C,V) : digit(V) } 1 :- index(R), index(C).

% No digit repeats in a row, in a column, or in a 3 x 3 box (a box is 3 cells wide for the 9 x 9 grid).
:- x(R,C1,V), x(R,C2,V), C1 < C2.
:- x(R1,C,V), x(R2,C,V), R1 < R2.
:- x(R1,C1,V), x(R2,C2,V), (R1,C1) < (R2,C2), R1 / 3 == R2 / 3, C1 / 3 == C2 / 3.

% in_cage(K, R, C): cell (R, C) belongs to cage K (0-based here).
in_cage(K,R-1,C-1) :- problem(K,1,J,0,R), problem(K,1,J,1,C).

% Each cage adds up to its target and holds different digits.
:- problem(K,0,Target), Target != #sum { V,R,C : in_cage(K,R,C), x(R,C,V) }.
:- in_cage(K,R1,C1), in_cage(K,R2,C2), (R1,C1) < (R2,C2), x(R1,C1,V), x(R2,C2,V).

#show x/3.
