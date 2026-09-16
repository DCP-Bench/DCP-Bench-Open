% Heterosquare: an n by n square of the distinct integers 1..n^2 whose row,
% column and diagonal sums are all different from each other.
cell(0..N-1) :- n(N).
value(1..N*N) :- n(N).

1 { x(I,J,V) : value(V) } 1 :- cell(I), cell(J).
% Every entry is distinct.
:- x(I,J,V), x(K,L,V), (I,J) < (K,L).

total(row(I), S) :- cell(I), S = #sum { V,J : x(I,J,V) }.
total(col(J), S) :- cell(J), S = #sum { V,I : x(I,J,V) }.
total(diag(1), S) :- S = #sum { V,I : x(I,I,V) }.
total(diag(2), S) :- n(N), S = #sum { V,I : x(I,J,V), J == N - I - 1 }.

% All of those sums differ.
:- total(P,S), total(Q,S), P < Q.

#show x/3.
