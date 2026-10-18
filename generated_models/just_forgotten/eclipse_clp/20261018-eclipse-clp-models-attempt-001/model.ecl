% Joe's account number: a permutation x of the digits 0..n-1, where each
% recorded set agrees with x in exactly num_correct_digits positions.
% The number of digits n and the number of sets come from the instance.

:- lib(ic).

model(Instance, Xs, [x-Xs], none) :-
    memberchk(sets-Sets, Instance),
    memberchk(num_correct_digits-K, Instance),
    Sets = [S0|_],
    length(S0, N),
    Max is N - 1,
    length(Xs, N),
    Xs :: 0..Max,

    % the account number has all the digits from 0 to n-1 in some order
    alldifferent(Xs),

    % in each set, exactly K digits are in their correct position
    ( foreach(S, Sets), param(Xs, K) do
        ( foreach(V, S), foreach(X, Xs), fromto(0, A0, A1, Count) do
            B #= (X #= V),
            A1 #= A0 + B
        ),
        Count #= K
    ).
