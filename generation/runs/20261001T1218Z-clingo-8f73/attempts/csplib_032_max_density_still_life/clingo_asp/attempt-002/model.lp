% Maximum density still life: on an n x m active grid inside Conway's Game of Life, find the stable
% pattern (still life) with the most live cells. Life is played on an infinite board: cells outside the
% grid are dead, but must not come alive either.
% Instance facts: n(N): rows of the grid; m(M): columns of the grid.
cell(0..N-1,0..M-1) :- n(N), m(M).

% board(X,Y): the cells of the grid and the ring of dead cells just outside it. Cells farther out
% have no live neighbour, so they can never come alive.
board(X,Y) :- n(N), m(M), X = -1..N, Y = -1..M.

% live(I,J): the grid cell (I,J) is alive.
{ live(I,J) } :- cell(I,J).

% column_ge(X,Y,K) holds when at least K of the three cells (X-1,Y), (X,Y), (X+1,Y), which form
% a vertical strip of the grid, are alive, K = 1..3. Neighbouring board cells share these strip
% counts, which gives the solver intermediate facts to learn about instead of eight separate neighbours.
column_ge(X,Y,K) :- board(X,Y), K = 1..3, K <= #count { A : live(A,Y), |A-X| <= 1 }.

% neighbours(X,Y,C): the board cell (X,Y) has C live neighbours. The three strips of columns
% Y-1, Y and Y+1 count the cell itself once if it is alive, so that one is taken off.
side(-1..1).
neighbours(X,Y,C) :- board(X,Y), C = #sum { 1,K,D : column_ge(X,Y+D,K), side(D) ; -1,self : live(X,Y) }.

% A live cell needs exactly 2 or 3 live neighbours to remain alive.
:- live(I,J), neighbours(I,J,C), C < 2.
:- live(I,J), neighbours(I,J,C), C > 3.

% A dead cell, in the grid or just outside it, must not have exactly 3 live neighbours, or it would become alive.
:- board(X,Y), not live(X,Y), neighbours(X,Y,3).

% Maximise the number of live cells in the grid.
#maximize { 1,I,J : live(I,J) }.

% grid(I,J,true/false): whether the cell (I,J) is alive.
grid(I,J,true)  :- live(I,J).
grid(I,J,false) :- cell(I,J), not live(I,J).

#show grid/3.
