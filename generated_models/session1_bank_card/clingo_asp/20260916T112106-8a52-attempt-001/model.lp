% Bank card: a four-digit PIN abcd where cd is three times ab and da is twice
% bc.
digit(0..9).

1 { a(D) : digit(D) } 1.
1 { b(D) : digit(D) } 1.
1 { c(D) : digit(D) } 1.
1 { d(D) : digit(D) } 1.

pin(pa,D) :- a(D).
pin(pb,D) :- b(D).
pin(pc,D) :- c(D).
pin(pd,D) :- d(D).
:- pin(X,D), pin(Y,D), X < Y.

:- a(A), b(B), c(C), d(D), 10 * C + D != 3 * (10 * A + B).
:- a(A), b(B), c(C), d(D), 10 * D + A != 2 * (10 * B + C).

#show a/1.
#show b/1.
#show c/1.
#show d/1.
