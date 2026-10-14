% Autoref: find a series s[0..n+1] in which every i from 0 to n occurs exactly
% s[i] times, and whose last element s[n+1] equals m.
position(0..N+1) :- n(N).

% Every position holds one value between 0 and n.
1 { s(K,V) : V = 0..N } 1 :- position(K), n(N).

% The last element is m.
:- n(N), m(M), not s(N+1,M).

% The value i occurs exactly s[i] times in the series.
:- n(N), I = 0..N, s(I,C), C != #count { K : s(K,I) }.

#show s/2.
