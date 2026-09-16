% Among: exactly m of the n entries of x take a value drawn from v; the rest
% are free within the domain.
position(0..N-1) :- n(N).
% Domain 0..7 comes from the problem statement, which fixes it for every
% instance; the reference declares the same range.
value(0..7).
wanted(V) :- v(_,V).

1 { x(I,D) : value(D) } 1 :- position(I).

hit(I,V) :- x(I,V), wanted(V).
hits(K) :- K = #count { I,V : hit(I,V) }.
:- hits(K), m(M), K != M.

#show x/2.
