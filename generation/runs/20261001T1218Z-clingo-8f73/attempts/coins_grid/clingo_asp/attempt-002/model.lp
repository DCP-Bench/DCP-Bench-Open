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

% weight(I, J, W): a coin in cell (I, J) costs W, its squared distance from the main diagonal.
weight(I,J,(I - J) * (I - J)) :- index(I), index(J).

% The cost of row I is counted in unit steps: row_cost_ge(I, V) holds when the coins of row I
% cost V or more together. The total cost, to be minimised, is the number of such steps over
% all rows. Counting in steps lets the solver see, while it searches, how much a row already
% costs and how much it must cost at the least; a single weighted sum over all cells cannot.
top_weight(I,M) :- index(I), M = #max { W : weight(I,_,W) }.
row_cost_ge(I,V) :- top_weight(I,M), c(C), V = 1..C * M,
                    V <= #sum { W,J : coin(I,J), weight(I,J,W) }.

% Implied by the row rule: a row with c coins costs at least as much as its c cheapest
% cells, the ones nearest the diagonal (ties broken by column). That many steps hold in
% every solution, so they are stated up front.
rank(I,J,R) :- weight(I,J,W), R = #count { K : weight(I,K,V), (V,K) < (W,J) }.
cheapest(I,S) :- index(I), c(C), S = #sum { W,J : rank(I,J,R), R < C, weight(I,J,W) }.
row_cost_ge(I,1..S) :- cheapest(I,S), S >= 1.

#minimize { 1,I,V : row_cost_ge(I,V) }.

% z is the total cost, the sum over all coins of the squared distance from the diagonal.
z(Z) :- Z = #count { I,V : row_cost_ge(I,V) }.

% x(I, J, 1) when the cell holds a coin and 0 when it is empty.
x(I,J,1) :- coin(I,J).
x(I,J,0) :- index(I), index(J), not coin(I,J).

#show x/3.
#show z/1.
