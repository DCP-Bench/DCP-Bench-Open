:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Divisible by 1 through 9: a ten-digit pandigital number whose first n digits
% form a multiple of n, for every n.
model(_Instance, Vars, [number-Number]) :-
    Digits = 10,
    length(Xs, Digits),
    Xs ins 0..9,
    all_distinct(Xs),
    length(Ts, Digits),
    Upper is 10 ^ Digits,
    Ts ins 0..Upper,
    append(Xs, Ts, Vars),
    last(Ts, Number),

    numlist(1, Digits, Positions),
    maplist({Xs, Ts}/[I]>>prefix_rule(Xs, Ts, I), Positions).

% The first I digits read as a number, which must divide by I exactly.
prefix_rule(Xs, Ts, I) :-
    length(Front, I),
    append(Front, _, Xs),
    numlist(1, I, Places),
    maplist({I}/[K, Weight]>>(Weight is 10 ^ (I - K)), Places, Weights),
    nth1(I, Ts, T),
    scalar_product(Weights, Front, #=, T),
    T mod I #= 0.
