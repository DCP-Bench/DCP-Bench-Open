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
% The groups are found by walking from the start to the end: group(A, B) is a group that
% holds the elements after boundary A up to boundary B. Every boundary reached on the way
% except the end starts the next group. The walk is written as a path because that way the
% size error of each group is a constant attached to one atom, which the search can add up
% and compare with the best answer so far.
boundary(0).
boundary(J) :- allowed(J).
boundary(N) :- len(N).
reached(0).
1 { group(A,B) : boundary(B), B > A } 1 :- reached(A), len(N), A < N.
reached(B) :- group(A,B).

% There are exactly K groups.
:- k(K), #count { A,B : group(A,B) } != K.

% step(P, B): the P-th boundary on the walk is B; the break points are the boundaries of the walk
% except the start and the end.
step(0,0).
step(P+1,B) :- step(P,A), group(A,B).

% x(P, J): the P-th break point (P = 0..K-2) is after the first J elements.
x(P-1,J) :- step(P,J), k(K), 1 <= P, P < K.

% error: the total difference between group sizes and the ideal size, to be minimised. The problem
% declares it to lie between 0 and N.
:- len(N), #sum { |B - A - G|,A,B : group(A,B), gsize(G) } > N.
#minimize { |B - A - G|,A,B : group(A,B), gsize(G) }.

#show x/2.
