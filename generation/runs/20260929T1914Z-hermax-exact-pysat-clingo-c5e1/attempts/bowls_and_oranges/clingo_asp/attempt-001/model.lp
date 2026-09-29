% Bowls and oranges: put oranges in bowls placed in a line, at most one per bowl,
% so that no three oranges are at equal distances from each other.
% n(N): number of bowls. m(M): number of oranges.
% x(I, P): the I-th orange, in ascending order, is in bowl P (1 to N).
1 { x(I,P) : P = 1..N } 1 :- n(N), m(M), I = 0..M-1.

% Ascending order: the next orange is in a later bowl, so every orange has its own bowl.
:- x(I,P), x(I+1,Q), P >= Q.

occupied(P) :- x(_,P).
% No three oranges A, B, C with B in the middle: there are no bowls P < Q with
% oranges in P, Q and in 2Q - P.
:- occupied(P), occupied(Q), P < Q, occupied(2*Q-P).

#show x/2.
