:- use_module(library(clpfd)).
:- use_module(library(lists)).

% Three sum: pick exactly m of the numbers so that they add up to zero.
model(Instance, Indices, [indices-Indices]) :-
    Nums = Instance.nums,
    M = Instance.m,
    length(Nums, N),
    length(Indices, N),
    Indices ins 0..1,
    scalar_product(Nums, Indices, #=, 0),
    sum(Indices, #=, M).
