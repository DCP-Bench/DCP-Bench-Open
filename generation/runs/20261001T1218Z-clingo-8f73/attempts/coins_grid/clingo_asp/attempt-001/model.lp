% Coins grid: place coins on an n by n grid, at most one per cell, with exactly c coins in
% every row and in every column, so that the sum over all coins of the squared horizontal
% distance to the main diagonal, (row - column)^2, is as small as possible.
% Instance facts: n(N): the size of the grid; c(C): the number of coins in each row and column.
index(0..N-1) :- n(N).

% coin(I, J): a coin lies in the cell of row I and column J.
{ coin(I,J) } :- index(I), index(J).

% Every row holds exactly c coins.
:- index(I), c(C), #count { J : coin(I,J) } != C.

% Every column holds exactly c coins.
:- index(J), c(C), #count { I : coin(I,J) } != C.

% The squared distance from the main diagonal of all cells holding a coin, to be minimised.
z(Z) :- Z = #sum { (I - J) * (I - J),I,J : coin(I,J) }.
#minimize { Z : z(Z) }.

% x(I, J, 1) when the cell holds a coin and 0 when it is empty.
x(I,J,1) :- coin(I,J).
x(I,J,0) :- index(I), index(J), not coin(I,J).

#show x/3.
#show z/1.
