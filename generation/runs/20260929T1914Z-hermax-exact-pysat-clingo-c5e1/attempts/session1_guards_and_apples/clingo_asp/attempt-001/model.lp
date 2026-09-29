% Guards and apples: a boy passes several gates. At each gate he gives the guard
% half of his apples plus one, and after the last gate one apple is left for the girl.
% num_gates(G): the number of gates. apples(I, V): the boy has V apples before
% gate I; the last one, I = G, is what he has after the last gate.
1 { apples(I,V) : V = 0..100 } 1 :- num_gates(G), I = 0..G.

% After the last gate the boy keeps the one apple he gives to the girl.
:- num_gates(G), not apples(G,1).

% At each gate the guard gets half of the apples plus one, so the boy is left with
% half of them minus one: before = 2 * (after + 1).
:- apples(I,Before), apples(I+1,After), Before != 2*(After+1).

#show apples/2.
