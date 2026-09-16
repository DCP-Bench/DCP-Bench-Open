:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Dudeney numbers: a perfect cube whose digits sum to its cube root.
model(Instance, Vars, [number-Number]) :-
    N = Instance.n,
    length(Digits, N),
    Digits ins 0..9,
    Upper is 10 ^ N - 1,
    Number in 0..Upper,
    RootMax is 9 * N,
    CubeRoot in 1..RootMax,
    append([Number, CubeRoot], Digits, Vars),

    Number #= CubeRoot * CubeRoot * CubeRoot,
    sum(Digits, #=, CubeRoot),
    % Place value: the first digit is the most significant.
    numlist(1, N, Places),
    maplist({N}/[I, Weight]>>(Weight is 10 ^ (N - I)), Places, Weights),
    scalar_product(Weights, Digits, #=, Number),
    Number #> 1.
