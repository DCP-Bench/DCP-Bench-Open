% Knight's tour: number the squares of an n by n chessboard from 0 to n*n-1 so that a knight
% can move from the square numbered k to the square numbered k+1 for every k, which makes the
% knight visit every square exactly once. The tour is open: it need not return to its start.
% Instance facts: n(N), the size of the chessboard.
index(0..N-1) :- n(N).
value(0..N * N - 1) :- n(N).
cell(R,C) :- index(R), index(C).

% x(R, C, V): the knight is on the square in row R and column C at move V. Every square
% gets one move number and every move number is used once, so each square is visited once.
1 { x(R,C,V) : value(V) } 1 :- cell(R,C).
1 { x(R,C,V) : cell(R,C) } 1 :- value(V).

% knight_move(R, C, R2, C2): a knight can jump between the two squares (one step in one
% direction and two in the other).
knight_move(R,C,R2,C2) :- cell(R,C), cell(R2,C2), |R - R2| * |C - C2| == 2.

% Every move except the last is followed by the next move number on a square a knight's jump away.
1 { x(R2,C2,V + 1) : knight_move(R,C,R2,C2) } 1 :- x(R,C,V), value(V + 1).

% Every move except the first is preceded by the previous move number a knight's jump away
% (this follows from the rule above, and is kept because it makes the search shorter).
1 { x(R2,C2,V - 1) : knight_move(R,C,R2,C2) } 1 :- x(R,C,V), value(V - 1).

#show x/3.
