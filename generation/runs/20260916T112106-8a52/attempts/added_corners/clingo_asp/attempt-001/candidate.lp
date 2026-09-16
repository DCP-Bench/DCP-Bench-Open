% Added corners: digits 1..8 around a ring, each square the sum of its two
% adjoining circles. Reading order is a b c / d _ e / f g h, so positions 2, 4,
% 5 and 7 are the squares.
digit(1..8).
slot(0..7).

1 { positions(I,D) : digit(D) } 1 :- slot(I).
:- positions(I,D), positions(J,D), I < J.

:- positions(1,B), positions(0,A), positions(2,C), B != A + C.
:- positions(3,D), positions(0,A), positions(5,F), D != A + F.
:- positions(4,E), positions(2,C), positions(7,H), E != C + H.
:- positions(6,G), positions(5,F), positions(7,H), G != F + H.

#show positions/2.
