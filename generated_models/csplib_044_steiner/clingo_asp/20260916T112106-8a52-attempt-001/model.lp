% Steiner triple system: n(n-1)/6 triples drawn from n items, no two triples
% sharing more than one item.
item(0..N-1) :- n(N).
nsets(S) :- n(N), S = N * (N - 1) / 6.
triple(0..S-1) :- nsets(S).
member(0..1).

1 { sets(I,J,V) : member(V) } 1 :- triple(I), item(J).

% Every triple holds exactly three items.
:- triple(I), not 3 = #count { J : sets(I,J,1) }.

% Two triples overlap in at most one item.
:- triple(I), triple(K), I < K, 2 <= #count { J : sets(I,J,1), sets(K,J,1) }.

#show sets/3.
