:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Devil's word: put a plus or minus sign in front of every number of a list so
% that the signed numbers add up to the given total.
model(Instance, Result, [result-Result]) :-
    Arr = Instance.arr,        % the numbers, in order
    Total = Instance.total,    % the sum the signed numbers must reach

    % Result[i] = arr[i] with its chosen sign: either -arr[i] or +arr[i]
    maplist([Value, Signed]>>(Negative is -Value, Signed in Negative \/ Value), Arr, Result),

    % the signed numbers add up to the total
    sum(Result, #=, Total).
