:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Cutting stock: apply the available cutting patterns often enough to fill
% every order, using as few raw rolls as possible.
model(Instance, Vars, [patterns_used-Used, min_rolls_cut-Rolls], min(Rolls)) :-
    NumPatterns = Instance.num_patterns,
    PerPattern = Instance.num_rolls_width,
    Orders = Instance.orders,
    length(Used, NumPatterns),
    % Usage bound 0..100 per pattern is the reference's declared domain.
    Used ins 0..100,
    Ceiling is NumPatterns * 100,
    Rolls in 0..Ceiling,
    Vars = [Rolls|Used],
    % num_rolls_width is indexed pattern-then-width, so reading per width needs
    % the transpose.
    transpose(PerPattern, ByWidth),
    maplist({Used}/[Counts, Order]>>scalar_product(Counts, Used, #>=, Order),
            ByWidth, Orders),
    sum(Used, #=, Rolls).
