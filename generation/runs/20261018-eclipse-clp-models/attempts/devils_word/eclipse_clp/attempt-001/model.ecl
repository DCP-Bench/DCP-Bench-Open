% Devil's word: given an array of integers, insert '+' or '-' before each
% integer so that the signed sum is the total. Output result: the array
% with the chosen signs applied (result[i] is +arr[i] or -arr[i]).

:- lib(ic).

% Signs[i] = 1 for '+', 0 for '-'.
% Xs[i] = arr[i] * (2*Signs[i] - 1), so Xs[i] is +arr[i] or -arr[i].
model(Instance, Signs, [result-Xs]) :-
    memberchk(arr-Arr, Instance),
    memberchk(total-Total, Instance),
    length(Arr, N),
    length(Signs, N),
    Signs :: 0..1,
    length(Xs, N),
    % insert '+' or '-' before each integer
    ( foreach(A, Arr), foreach(S, Signs), foreach(X, Xs) do
        X #= A * (2*S - 1)
    ),
    % the signed values sum to the total
    sum(Xs) #= Total.
