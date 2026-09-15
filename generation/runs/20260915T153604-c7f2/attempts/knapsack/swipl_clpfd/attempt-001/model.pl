:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

% Knapsack: pick items to maximize total value without exceeding the pack's
% weight capacity.
model(Instance, Take, [x-Take], max(Value)) :-
    Values = Instance.values,
    Weights = Instance.weights,
    Capacity = Instance.capacity,
    length(Values, N),
    length(Take, N),
    Take ins 0..1,
    scalar_product(Weights, Take, #=<, Capacity),
    scalar_product(Values, Take, #=, Value).
