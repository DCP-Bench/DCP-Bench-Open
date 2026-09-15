:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Bin packing: assign each item to a bin without overloading any bin.
model(Instance, Bins, [bins-Bins]) :-
    Weights = Instance.weights,
    Capacity = Instance.capacity,
    NumBins = Instance.num_bins,
    length(Weights, N),
    length(Bins, N),
    Top is NumBins - 1,
    Bins ins 0..Top,
    % The reference ranges the capacity constraint over the item count rather
    % than the bin count; indices beyond num_bins - 1 are then vacuous.  Mirror
    % that range so the two models constrain exactly the same bins.
    Last is N - 1,
    numlist(0, Last, BinIndices),
    maplist({Bins, Weights, Capacity}/[I]>>load(Bins, Weights, Capacity, I),
            BinIndices).

load(Bins, Weights, Capacity, I) :-
    maplist({I}/[B, Here]>>(B #= I #<==> Here), Bins, Heres),
    scalar_product(Weights, Heres, #=<, Capacity).
