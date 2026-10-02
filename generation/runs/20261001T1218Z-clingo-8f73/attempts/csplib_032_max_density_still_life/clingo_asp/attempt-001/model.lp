% Maximum density still life: on an n x m active grid inside Conway's Game of Life, find the stable
% pattern (still life) with the most live cells. Life is played on an infinite board: cells outside the
% grid are dead, but must not come alive either.
% Instance facts: n(N): rows of the grid; m(M): columns of the grid.
cell(0..N-1,0..M-1) :- n(N), m(M).

% outside(X,Y): a dead cell just outside the active grid, in the ring around it. Cells farther out
% have no live neighbour and the corners of the ring have at most one, so only the sides matter, but
% all the ring cells are listed because it is simpler and gives the same rules.
outside(X,Y) :- n(N), m(M), X = -1..N, Y = -1..M, not cell(X,Y).

% next(X,Y,A,B): cell (A,B) of the grid is one of the up to eight neighbours of the board cell (X,Y).
next(X,Y,A,B) :- cell(X,Y), cell(A,B), (A,B) != (X,Y), |A-X| <= 1, |B-Y| <= 1.
next(X,Y,A,B) :- outside(X,Y), cell(A,B), |A-X| <= 1, |B-Y| <= 1.

% live(I,J): the grid cell (I,J) is alive.
{ live(I,J) } :- cell(I,J).

% A live cell needs exactly 2 or 3 live neighbours to remain alive.
:- live(I,J), #count { A,B : next(I,J,A,B), live(A,B) } < 2.
:- live(I,J), #count { A,B : next(I,J,A,B), live(A,B) } > 3.

% A dead cell must not have exactly 3 live neighbours, or it would become alive.
:- cell(I,J), not live(I,J), #count { A,B : next(I,J,A,B), live(A,B) } == 3.

% The same holds for the dead cells just outside the grid.
:- outside(X,Y), #count { A,B : next(X,Y,A,B), live(A,B) } == 3.

% Maximise the number of live cells in the grid.
#maximize { 1,I,J : live(I,J) }.

% grid(I,J,true/false): whether the cell (I,J) is alive.
grid(I,J,true)  :- live(I,J).
grid(I,J,false) :- cell(I,J), not live(I,J).

#show grid/3.
