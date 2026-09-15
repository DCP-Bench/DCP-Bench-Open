:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Money change: make the amount exactly from the coins on hand, using as few
% coins as possible.
model(Instance, Counts, [coin_counts-Counts], min(Total)) :-
    Amount = Instance.amount,
    Types = Instance.types_of_coins,
    Available = Instance.available_coins,
    length(Types, N),
    length(Counts, N),
    max_list(Available, MaxAvailable),
    Counts ins 0..MaxAvailable,
    maplist([Count, Cap]>>(Count #=< Cap), Counts, Available),
    scalar_product(Types, Counts, #=, Amount),
    sum(Counts, #=, Total).
