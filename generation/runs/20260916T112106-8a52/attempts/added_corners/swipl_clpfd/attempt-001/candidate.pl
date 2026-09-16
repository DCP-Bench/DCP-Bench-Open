:- use_module(library(clpfd)).

% Added corners: digits 1..8 around a ring, each square the sum of its two
% adjoining circles.  Reading order is a b c / d _ e / f g h.
model(_Instance, Positions, [positions-Positions]) :-
    length(Positions, 8),
    Positions ins 1..8,
    all_distinct(Positions),
    Positions = [A, B, C, D, E, F, G, H],
    B #= A + C,
    D #= A + F,
    E #= C + H,
    G #= F + H.
