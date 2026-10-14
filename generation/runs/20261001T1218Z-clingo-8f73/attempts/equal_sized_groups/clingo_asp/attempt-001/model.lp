% Equal sized groups: split a sorted list of N elements into K groups by choosing K-1 break
% points between them, so that equal values stay in the same group and the group sizes are as
% close as possible to round(N/K), measured by the sum of the size differences.
% Instance facts: a(I, V): element I (0-based) has value V, k(K): the number of groups.
len(N) :- N = #count { I : a(I,_) }.

% The ideal group size is round(N/K), rounding halves to the even number as Python's round does
% (the problem reference uses it).
gsize(Q)   :- len(N), k(K), Q = N / K, 2 * (N \ K) < K.
gsize(Q+1) :- len(N), k(K), Q = N / K, 2 * (N \ K) > K.
gsize(Q)   :- len(N), k(K), Q = N / K, 2 * (N \ K) == K, Q \ 2 == 0.
gsize(Q+1) :- len(N), k(K), Q = N / K, 2 * (N \ K) == K, Q \ 2 == 1.

% allowed(J): the 1-based break point J puts the first J elements before the break. Equal
% neighbouring values must stay in the same group, so a break between elements J-1 and J
% (0-based) is allowed only where their values differ.
allowed(J) :- a(J-1,V1), a(J,V2), V1 != V2.

% x(P, J): the P-th break point (P = 0..K-2) is after the first J elements.
1 { x(P,J) : allowed(J) } 1 :- k(K), P = 0..K-2.

% The break points are in strictly increasing order, so no group is empty.
:- x(P,J), x(P+1,J2), J2 <= J.

% The groups lie between consecutive break points: edge(P, E) is the end of group P-1 and
% the start of group P, with 0 before the first group and N after the last.
edge(0,0).
edge(P+1,J) :- x(P,J).
edge(K,N) :- k(K), len(N).

% size(P, S): group P holds S elements.
size(P,S) :- edge(P,A), edge(P+1,B), S = B - A.

% error: the total difference between group sizes and the ideal size, to be minimised. The problem
% declares it to lie between 0 and N.
error(E) :- E = #sum { |S - G|,P : size(P,S), gsize(G) }.
:- error(E), len(N), E > N.
#minimize { E : error(E) }.

#show x/2.
