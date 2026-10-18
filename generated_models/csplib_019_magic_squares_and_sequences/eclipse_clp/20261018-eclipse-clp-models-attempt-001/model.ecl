% CSPLib 019: magic sequences.
% A magic sequence of length n is a sequence of integers x_0, ..., x_{n-1} between 0 and n-1,
% such that for all i in 0 to n-1, the number i occurs exactly x_i times in the sequence.
% Output: the magic sequence x.

:- lib(ic).
:- lib(listut).

model(Instance, Xs, [x-Xs]) :-
    memberchk(n-N, Instance),
    length(Xs, N),
    Max is N - 1,
    Xs :: 0..Max,
    % for all i in 0 to n-1, the number i occurs exactly x_i times in the sequence
    ( for(I, 0, Max), param(Xs) do
        count_occurrences(I, Xs)
    ).

% the number I occurs exactly x_I times in the sequence
count_occurrences(I, Xs) :-
    nth0(I, Xs, Xi),
    indicator_list(Xs, I, Bs),
    sum(Bs) #= Xi.

% B_j is 1 exactly when x_j = I
indicator_list(Xs, I, Bs) :-
    ( foreach(X, Xs), foreach(B, Bs), param(I) do
        B #= (X #= I)
    ).
