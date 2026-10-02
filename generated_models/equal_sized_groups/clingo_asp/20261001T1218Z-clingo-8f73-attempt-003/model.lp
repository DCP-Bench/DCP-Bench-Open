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

% A boundary is the start of the list (0), the end of the list (N) or an allowed break point.
boundary(J) :- allowed(J).

% An upper bound on the smallest total error, from a plain choice of break points: the P-th break
% is the allowed point nearest to P*N/K (distances are scaled by K to stay whole numbers; the
% smallest point wins a tie). If these points increase, they are a valid answer, and its error is
% the bound; otherwise the bound is N, which is the most the problem allows the error to be.
dist(P,J,D) :- k(K), len(N), P = 1..K - 1, allowed(J), D = |J * K - P * N|.
nearest(P,D) :- k(K), P = 1..K - 1, dist(P,_,_), D = #min { E : dist(P,_,E) }.
pick(P,J) :- nearest(P,D), J = #min { I : dist(P,I,D) }.
bad :- k(K), P = 1..K - 1, not pick(P,_).
bad :- pick(P,J), pick(P + 1,J2), J2 <= J.
chosen(0,0).
chosen(P,J) :- pick(P,J).
chosen(K,N) :- k(K), len(N).
simple_error(C) :- not bad, C = #sum { |B2 - B1 - G|,P : chosen(P,B1), chosen(P + 1,B2), gsize(G) }.
bound(U) :- U = #min { N : len(N) ; C : simple_error(C) }.

% The groups are found by walking through the breaks: node(P, B) says the P-th boundary of the
% walk (P = 0..K, with boundary 0 the start and boundary K the end) is B, so that group P holds
% the elements after B up to the next node. A boundary can be on the walk only where it can lead
% to a total error within the bound: the error is at least the distance of the walk from
% the position P*G (G the ideal size) at boundary P plus the distance back to the position
% where the walk has to end, N - K*G.
candidate(0,0).
candidate(K,N) :- k(K), len(N).
candidate(P,B) :- k(K), P = 1..K - 1, boundary(B), bound(U), gsize(G), len(N),
                  |B - P * G| + |N - K * G - (B - P * G)| <= U.

node(0,0).
1 { node(P + 1,B) : candidate(P + 1,B), B > A } 1 :- node(P,A), k(K), P < K.
:- k(K), len(N), not node(K,N).

% The total error is within the bound, so no group is further from the ideal size than the bound.
% This loses no best answer, because the bound is the error of an answer or the largest error allowed.
:- bound(U), #sum { |B - A - G|,P : node(P,A), node(P + 1,B), gsize(G) } > U.
:- node(P,A), node(P + 1,B), gsize(G), bound(U), |B - A - G| > U.

% x(P, J): the P-th break point (P = 0..K-2) is after the first J elements.
x(P-1,B) :- node(P,B), k(K), 1 <= P, P < K.

% error: the total difference between group sizes and the ideal size, to be minimised.
#minimize { |B - A - G|,P : node(P,A), node(P + 1,B), gsize(G) }.

#show x/2.
