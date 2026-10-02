% Solitaire battleships: fill a grid with water, submarines and the parts of longer ships
% (left, right, top, bottom, middle) so that the fleet is complete, no two ships touch, not even
% at a corner, the numbers of ship squares in the rows and columns are met, and the squares
% given as hints hold.
% Instance facts: rows(R), cols(C); rowsum(I, S) and colsum(J, S): the number of ship squares in
% row I and column J; fleet_counts(K, 0, Size) and fleet_counts(K, 1, N): the fleet holds N ships
% of size Size; hints(K, 0, R), hints(K, 1, C), hints(K, 2, V): square (R, C) holds the code V;
% water(V), circle(V), left(V), right(V), top(V), bottom(V), middle(V): the codes of the kinds
% of square (circle is a submarine). The code _SHIP is not a kind of square of the puzzle
% statement and is never used.
cell(R,C) :- rows(M), cols(N), R = 0..M-1, C = 0..N-1.
kind(V) :- water(V).
kind(V) :- circle(V).
kind(V) :- left(V).
kind(V) :- right(V).
kind(V) :- top(V).
kind(V) :- bottom(V).
kind(V) :- middle(V).

% grid(R, C, V): square (R, C) has code V; every square has exactly one.
1 { grid(R,C,V) : kind(V) } 1 :- cell(R,C).

% A square is occupied when it is not water. Squares off the grid are never occupied.
occupied(R,C) :- cell(R,C), grid(R,C,V), not water(V).

% The hints: the given squares have the given codes.
:- hints(K,0,R), hints(K,1,C), hints(K,2,V), not grid(R,C,V).

% The numbers of occupied squares in each row and in each column are as indicated.
:- rowsum(R,S), S != #count { C : occupied(R,C) }.
:- colsum(C,S), S != #count { R : occupied(R,C) }.

% No two ships touch at a corner: no two occupied squares are diagonal neighbours.
:- occupied(R,C), occupied(R + 1,C + 1).
:- occupied(R,C), occupied(R + 1,C - 1).

% Squares that can stand next to a part of a ship, in the line of the ship: horizontally a left
% or middle part can stand before the next part, and a right or middle part after the previous
% one; vertically a top or middle part before, and a bottom or middle part after.
head_h(R,C) :- grid(R,C,V), left(V).
head_h(R,C) :- grid(R,C,V), middle(V).
tail_h(R,C) :- grid(R,C,V), right(V).
tail_h(R,C) :- grid(R,C,V), middle(V).
head_v(R,C) :- grid(R,C,V), top(V).
head_v(R,C) :- grid(R,C,V), middle(V).
tail_v(R,C) :- grid(R,C,V), bottom(V).
tail_v(R,C) :- grid(R,C,V), middle(V).

% A submarine is surrounded by water on all four sides.
orthogonal(-1,0).
orthogonal(1,0).
orthogonal(0,-1).
orthogonal(0,1).
:- grid(R,C,V), circle(V), orthogonal(DR,DC), occupied(R + DR,C + DC).

% A left end continues to the right (middle or right part) and has water on its other three sides.
:- grid(R,C,V), left(V), not tail_h(R,C + 1).
:- grid(R,C,V), left(V), occupied(R,C - 1).
:- grid(R,C,V), left(V), occupied(R - 1,C).
:- grid(R,C,V), left(V), occupied(R + 1,C).

% A right end continues to the left (middle or left part) and has water on its other three sides.
:- grid(R,C,V), right(V), not head_h(R,C - 1).
:- grid(R,C,V), right(V), occupied(R,C + 1).
:- grid(R,C,V), right(V), occupied(R - 1,C).
:- grid(R,C,V), right(V), occupied(R + 1,C).

% A top end continues downwards (middle or bottom part) and has water on its other three sides.
:- grid(R,C,V), top(V), not tail_v(R + 1,C).
:- grid(R,C,V), top(V), occupied(R - 1,C).
:- grid(R,C,V), top(V), occupied(R,C - 1).
:- grid(R,C,V), top(V), occupied(R,C + 1).

% A bottom end continues upwards (middle or top part) and has water on its other three sides.
:- grid(R,C,V), bottom(V), not head_v(R - 1,C).
:- grid(R,C,V), bottom(V), occupied(R + 1,C).
:- grid(R,C,V), bottom(V), occupied(R,C - 1).
:- grid(R,C,V), bottom(V), occupied(R,C + 1).

% A middle part lies in a horizontal ship (ship parts left and right of it, water above and
% below) or in a vertical ship (ship parts above and below it, water left and right of it).
horizontal_middle(R,C) :- grid(R,C,V), middle(V), head_h(R,C - 1), tail_h(R,C + 1),
                          not occupied(R - 1,C), not occupied(R + 1,C).
vertical_middle(R,C) :- grid(R,C,V), middle(V), head_v(R - 1,C), tail_v(R + 1,C),
                        not occupied(R,C - 1), not occupied(R,C + 1).
:- grid(R,C,V), middle(V), not horizontal_middle(R,C), not vertical_middle(R,C).

% The fleet: the number of submarines is the number of ships of size 1.
:- fleet_counts(K,0,1), fleet_counts(K,1,N), N != #count { R,C : grid(R,C,V), circle(V) }.

% A longer ship is a left end, some middle parts and a right end in a row, or a top end, some
% middle parts and a bottom end in a column. span_h(R, C, E): from the left end at (R, C) the
% middle parts reach up to column E; span_v is the same downwards.
span_h(R,C,C) :- grid(R,C,V), left(V).
span_h(R,C,E + 1) :- span_h(R,C,E), grid(R,E + 1,V), middle(V).
span_v(R,C,R) :- grid(R,C,V), top(V).
span_v(R,C,E + 1) :- span_v(R,C,E), grid(E + 1,C,V), middle(V).

% ship_h(R, C, Size) and ship_v(R, C, Size): a ship of that size starts at (R, C).
ship_h(R,C,E + 2 - C) :- span_h(R,C,E), grid(R,E + 1,V), right(V).
ship_v(R,C,E + 2 - R) :- span_v(R,C,E), grid(E + 1,C,V), bottom(V).

% Each size of ship longer than 1 occurs as often as the fleet says.
:- fleet_counts(K,0,Size), Size >= 2, fleet_counts(K,1,N),
   N != #count { h,R,C : ship_h(R,C,Size) ; v,R,C : ship_v(R,C,Size) }.

% No ship of a size the fleet does not list: every left or top end begins one of the ships counted.
:- N = #sum { Cnt,K : fleet_counts(K,0,Size), Size >= 2, fleet_counts(K,1,Cnt) },
   N != #count { h,R,C : grid(R,C,V), left(V) ; v,R,C : grid(R,C,V), top(V) }.

#show grid/3.
