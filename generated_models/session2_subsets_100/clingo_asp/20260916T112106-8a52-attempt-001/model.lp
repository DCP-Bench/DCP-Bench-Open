% Split A into two disjoint non-empty subsets S and T with equal sums. The
% instance field is a bare capital, which the runner lowers to a/2.
idx(I) :- a(I,_).
member(0..1).

1 { in_S(I,V) : member(V) } 1 :- idx(I).
1 { in_T(I,V) : member(V) } 1 :- idx(I).

sum_s(X) :- X = #sum { W,I : in_S(I,1), a(I,W) }.
sum_t(X) :- X = #sum { W,I : in_T(I,1), a(I,W) }.
:- sum_s(X), sum_t(Y), X != Y.

% Disjoint: no element lands in both subsets.
:- in_S(I,1), in_T(I,1).

% Both subsets are non-empty.
:- not 1 <= #count { I : in_S(I,1) }.
:- not 1 <= #count { I : in_T(I,1) }.

#show in_S/2.
#show in_T/2.
