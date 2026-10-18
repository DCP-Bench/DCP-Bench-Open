% Ages of the sons: an old man has three sons. Find their ages (oldest first)
% from the puzzle clues. Outputs A1 >= A2 >= A3 are the ages of the sons.

:- lib(ic).

% All ages triples (oldest first) whose product is 36. This is the search space
% the first clue leaves open; it is built from the description, not from an answer.
candidates(Cands) :-
    findall(t(P, Q, R),
            ( rng(1, 36, P), rng(1, P, Q), rng(1, Q, R),
              P * Q * R =:= 36 ),
            Cands).

% rng(Lo, Hi, X): X runs over Lo..Hi (between/3 is not in the ECLiPSe image).
rng(L, H, L) :- L =< H.
rng(L, H, X) :- L < H, L1 is L + 1, rng(L1, H, X).

model(_Instance, [Idx], ['A1'-X1, 'A2'-X2, 'A3'-X3], none) :-
    candidates(Cands),
    length(Cands, K),
    findall(P, member(t(P, _, _), Cands), Ps),
    findall(Q, member(t(_, Q, _), Cands), Qs),
    findall(R, member(t(_, _, R), Cands), Rs),
    findall(S, ( member(t(P, Q, R), Cands), S is P + Q + R ), Sums),
    % 1 when that triple has a unique oldest son (P > Q), else 0
    findall(U, ( member(t(P, Q, _), Cands), ( P > Q -> U = 1 ; U = 0 ) ), Us),
    findall(I, rng(1, K, I), Is),
    Idx :: 1..K,
    element(Idx, Ps, X1),
    element(Idx, Qs, X2),
    element(Idx, Rs, X3),
    element(Idx, Sums, Sum),
    % The sum of their ages equals the number of windows, which is not given,
    % so Sum is free apart from the clues below.

    % The mathematician said: "I need more information."
    % The sum does not identify the triple: at least two triples share it.
    length(Bs, K),
    ( foreach(Sk, Sums), foreach(Bk, Bs), param(Sum) do
        Bk #= (Sk #= Sum)
    ),
    sum(Bs) #>= 2,

    % The oldest son has blue eyes. The mathematician said: "I got it."
    % The oldest son is unique, and among the triples with this sum and a
    % unique oldest son, only one is left (the chosen one).
    element(Idx, Us, 1),
    ( foreach(Sk, Sums), foreach(Uk, Us), foreach(Ik, Is), param(Sum, Idx) do
        ( (Uk #= 1) and (Sk #= Sum) ) => (Ik #= Idx)
    ).
