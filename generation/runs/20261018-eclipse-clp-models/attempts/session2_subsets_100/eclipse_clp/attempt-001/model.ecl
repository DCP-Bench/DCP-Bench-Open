% session2_subsets_100: from a set A of distinct integers, find two disjoint
% non-empty subsets S and T whose elements have equal sums. Output in_S and in_T
% as 0/1 membership lists of the same length as A.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, Outputs) :-
    memberchk('A'-As, Instance),
    length(As, N),
    length(InS, N), InS :: 0..1,
    length(InT, N), InT :: 0..1,

    % Two disjoint subsets: no element of A is in both S and T.
    ( foreach(S, InS), foreach(T, InT) do
        S + T #=< 1
    ),

    % Both subsets are non-empty.
    sum(InS) #>= 1,
    sum(InT) #>= 1,

    % The sum of the elements of S equals the sum of the elements of T.
    ( foreach(A, As), foreach(S, InS), foreach(P, Ps) do
        P #= A * S
    ),
    ( foreach(A, As), foreach(T, InT), foreach(Q, Qs) do
        Q #= A * T
    ),
    sum(Ps) #= sum(Qs),

    append(InS, InT, Vars),
    Outputs = [in_S-InS, in_T-InT].
