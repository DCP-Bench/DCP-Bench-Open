% Hidato: a grid is partly filled with numbers. Fill the empty cells so that every number from 1
% to the number of cells is used once and each number touches the next one horizontally,
% vertically or diagonally.
% Instance facts: puzzle(R, C, V): the cell in row R and column C holds V, or 0 if it is empty.
cell(R,C) :- puzzle(R,C,_).
total(N) :- N = #count { R,C : cell(R,C) }.

% x(R, C, V): the cell in row R and column C holds the number V. Each cell holds one number
% from 1 to the number of cells, and every number is used exactly once.
1 { x(R,C,V) : V = 1..N } 1 :- cell(R,C), total(N).
1 { x(R,C,V) : cell(R,C) } 1 :- total(N), V = 1..N.

% The numbers already filled in stay where they are (0 marks an empty cell).
:- puzzle(R,C,V), V > 0, not x(R,C,V).

% touches(R, C, R2, C2): two different cells are next to each other horizontally,
% vertically or diagonally.
touches(R,C,R2,C2) :- cell(R,C), cell(R2,C2), |R - R2| <= 1, |C - C2| <= 1, |R - R2| + |C - C2| > 0.

% Each number except the last has the next number in a touching cell.
:- x(R,C,V), total(N), V < N, #count { R2,C2 : touches(R,C,R2,C2), x(R2,C2,V + 1) } == 0.

#show x/3.
