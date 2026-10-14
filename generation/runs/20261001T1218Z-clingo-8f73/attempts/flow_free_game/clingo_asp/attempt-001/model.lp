% Flow Free: connect matching colours with pipes so that every cell of the board is covered.
% Instance: board(I, J, C) is the colour C at row I, column J (counted from 0), or 0 when the
% cell is empty and has to be filled. The output b(I, J, C) gives the colour of every cell.

cell(I,J) :- board(I,J,_).
% The cells directly above, below, left and right of a cell.
neighbour(I,J,K,L) :- cell(I,J), cell(K,L), |K - I| + |L - J| = 1.

% The colours are those of the pipe ends on the board. (The reference lets a cell take a value up
% to 10, which would also allow closed loops of a colour with no pipe end; the statement asks for
% colours 1 to 5, the colours on the board, so only those are used.)
colour(C) :- board(_,_,C), C > 0.

% b(I, J, C): cell (I, J) has colour C.
1 { b(I,J,C) : colour(C) } 1 :- cell(I,J).

% A cell that already has a colour keeps it.
:- board(I,J,C), C > 0, not b(I,J,C).

% A pipe end continues into exactly one neighbouring cell of its colour.
:- board(I,J,C), C > 0, #count { K,L : neighbour(I,J,K,L), b(K,L,C) } != 1.

% An empty cell is part of a pipe, so it has exactly two neighbours of its own colour: the
% cells before and after it along the pipe.
:- board(I,J,0), b(I,J,C), #count { K,L : neighbour(I,J,K,L), b(K,L,C) } != 2.

#show b/3.
