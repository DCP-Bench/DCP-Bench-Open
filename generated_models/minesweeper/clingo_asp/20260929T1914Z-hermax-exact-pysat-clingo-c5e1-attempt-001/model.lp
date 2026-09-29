% Minesweeper: from the revealed numbers of a board, decide which of the
% unopened cells hold a mine. An opened cell is safe and shows how many of its
% (up to eight) neighbours are mines.
cell(R,C) :- game_data(R,C,_).

% Any cell may hold a mine; mines/3 reports 1 for a mine and 0 for none.
{ mine(R,C) } :- cell(R,C).
mines(R,C,1) :- mine(R,C).
mines(R,C,0) :- cell(R,C), not mine(R,C).

% An opened cell (its value is not the "unopened" marker x) is not a mine ...
:- x(X), game_data(R,C,V), V != X, mine(R,C).
% ... and its number is the count of mines among its neighbours.
:- x(X), game_data(R,C,V), V != X,
   V != #count { A,B : mine(A,B), |A - R| <= 1, |B - C| <= 1, (A,B) != (R,C) }.

#show mines/3.
