% Solitaire Battleships (CSPLib 14): place a fleet of horizontal or vertical ships on a
% grid so that no two ships touch, not even diagonally, the number of occupied cells in
% each row and column matches the given sums, and the given shots (hints) are respected.
% Output grid(R, C, V): cell (R, C) holds code V, one of water, submarine (circle), or a
% ship part (left, right, top, bottom, middle); the codes come from the instance fields.

cell(R,C) :- R = 0..Rs-1, C = 0..Cs-1, rows(Rs), cols(Cs).

% The cell codes 0..7 are the domain the reference declares for the grid. Code _SHIP (a
% ship part of unspecified kind) is in that domain, so a cell may take it as in the reference.
value(0..7).

% kind(K, V): code V means piece kind K. The fields WATER, _SHIP, CIRCLE, ... arrive
% lowered as wATER/1, _sHIP/1, cIRCLE/1, ...
kind(water,V) :- wATER(V).
kind(ship,V) :- _sHIP(V).
kind(circle,V) :- cIRCLE(V).
kind(left,V) :- lEFT(V).
kind(right,V) :- rIGHT(V).
kind(top,V) :- tOP(V).
kind(bottom,V) :- bOTTOM(V).
kind(middle,V) :- mIDDLE(V).

% Each cell holds exactly one code.
1 { grid(R,C,V) : value(V) } 1 :- cell(R,C).

% is(R, C, K): cell (R, C) holds a piece of kind K.
is(R,C,K) :- grid(R,C,V), kind(K,V).

% occupied(R, C): the cell holds any code above WATER, which counts as a ship segment.
occupied(R,C) :- grid(R,C,V), wATER(W), V > W.

% open(R, C): cell (R, C) is water or lies off the grid. A neighbour that must be water
% when it exists is required to be open; the ring of off-grid cells is open.
open(R,C) :- is(R,C,water).
open(R,C) :- R = -1..Rs, C = -1..Cs, rows(Rs), cols(Cs), not cell(R,C).

% Hints: a shot fixes the code of its cell.
:- hints(I,0,R), hints(I,1,C), hints(I,2,V), not grid(R,C,V).

% Row and column sums: the number of ship segments in each row and column.
:- rowsum(R,S), #count { C : occupied(R,C) } != S.
:- colsum(C,S), #count { R : occupied(R,C) } != S.

% No diagonal or corner-touching ships: the diagonal neighbours of a ship segment are water.
:- occupied(R,C), DR = -1..1, DC = -1..1, DR != 0, DC != 0, not open(R+DR,C+DC).

% A submarine (circle) is entirely surrounded by water.
:- is(R,C,circle), not open(R-1,C).
:- is(R,C,circle), not open(R+1,C).
:- is(R,C,circle), not open(R,C-1).
:- is(R,C,circle), not open(R,C+1).

% Parts that may follow a left end or precede a right end, and likewise vertically.
after_left(R,C) :- is(R,C,middle).
after_left(R,C) :- is(R,C,right).
before_right(R,C) :- is(R,C,middle).
before_right(R,C) :- is(R,C,left).
after_top(R,C) :- is(R,C,middle).
after_top(R,C) :- is(R,C,bottom).
before_bottom(R,C) :- is(R,C,middle).
before_bottom(R,C) :- is(R,C,top).

% A left end has a middle or right part to its right, and water left, above and below.
:- is(R,C,left), not after_left(R,C+1).
:- is(R,C,left), not open(R,C-1).
:- is(R,C,left), not open(R-1,C).
:- is(R,C,left), not open(R+1,C).

% A right end has a middle or left part to its left, and water right, above and below.
:- is(R,C,right), not before_right(R,C-1).
:- is(R,C,right), not open(R,C+1).
:- is(R,C,right), not open(R-1,C).
:- is(R,C,right), not open(R+1,C).

% A top end has a middle or bottom part below it, and water above, left and right.
:- is(R,C,top), not after_top(R+1,C).
:- is(R,C,top), not open(R-1,C).
:- is(R,C,top), not open(R,C-1).
:- is(R,C,top), not open(R,C+1).

% A bottom end has a middle or top part above it, and water below, left and right.
:- is(R,C,bottom), not before_bottom(R-1,C).
:- is(R,C,bottom), not open(R+1,C).
:- is(R,C,bottom), not open(R,C-1).
:- is(R,C,bottom), not open(R,C+1).

% A middle part is either horizontal (left end or middle on its left, right end or middle
% on its right, water above and below) or vertical (the same turned a quarter).
horizontal_middle(R,C) :- is(R,C,middle), before_right(R,C-1), after_left(R,C+1),
                          open(R-1,C), open(R+1,C).
vertical_middle(R,C) :- is(R,C,middle), before_bottom(R-1,C), after_top(R+1,C),
                        open(R,C-1), open(R,C+1).
:- is(R,C,middle), not horizontal_middle(R,C), not vertical_middle(R,C).

% Fleet composition. fleet(Size, Count) reads the [size, count] pairs.
fleet(S,K) :- fleet_counts(I,0,S), fleet_counts(I,1,K).

% Submarines: the number of circles is the count listed for size 1.
:- fleet(1,K), #count { R,C : is(R,C,circle) } != K.

% A ship of size n is an end piece, n-2 middle pieces and the other end piece in one line.
% hrun(R, C, L): a left end at (R, C) followed by L-1 middle pieces; a right end after it
% completes a horizontal ship of size L+1 starting at (R, C). The same vertically.
hrun(R,C,1) :- is(R,C,left).
hrun(R,C,L+1) :- hrun(R,C,L), is(R,C+L,middle).
ship(R,C,h,L+1) :- hrun(R,C,L), is(R,C+L,right).
vrun(R,C,1) :- is(R,C,top).
vrun(R,C,L+1) :- vrun(R,C,L), is(R+L,C,middle).
ship(R,C,v,L+1) :- vrun(R,C,L), is(R+L,C,bottom).

% Each listed size of 2 or more has exactly its listed number of ships.
:- fleet(S,K), S >= 2, #count { R,C,D : ship(R,C,D,S) } != K.

% No ship of a size the fleet does not list: the left and top ends number exactly the
% ships of size 2 or more that the fleet lists.
:- T = #sum { K,S : fleet(S,K), S > 1 }, #count { R,C,left : is(R,C,left); R,C,top : is(R,C,top) } != T.

#show grid/3.
