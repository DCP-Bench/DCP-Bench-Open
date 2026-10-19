% 0/1 knapsack: a hiker chooses which items to take in a backpack.
% Each item has a value and a weight; maximise the total value of the
% items taken without exceeding the weight capacity.
% Output x: list of booleans, true when the item is taken.

:- lib(ic).

model(Instance, Xs, [x-Xs], max(sum(Products))) :-
    memberchk(capacity-Capacity, Instance),
    memberchk(values-Values, Instance),
    memberchk(weights-Weights, Instance),
    length(Values, N),
    length(Xs, N),
    Xs :: 0..1,
    % each item has a certain value and weight: the product of the item's
    % weight and its taken flag is the weight carried for that item
    ( foreach(W, Weights), foreach(X, Xs), foreach(WX, WeightedTaken) do
        WX #= W * X
    ),
    % without exceeding the weight capacity of the backpack
    sum(WeightedTaken) #=< Capacity,
    % maximize the total value of the items in the backpack
    ( foreach(V, Values), foreach(X, Xs), foreach(P, Products) do
        P #= V * X
    ).
