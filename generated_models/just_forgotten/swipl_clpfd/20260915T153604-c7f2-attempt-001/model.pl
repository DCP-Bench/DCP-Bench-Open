:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Just forgotten: recover a permutation of the digits, given several guesses
% that each got the same number of positions right.
model(Instance, Xs, [x-Xs]) :-
    Sets = Instance.sets,
    NumCorrect = Instance.num_correct_digits,
    Sets = [FirstGuess|_],
    length(FirstGuess, N),
    length(Xs, N),
    Top is N - 1,
    Xs ins 0..Top,
    all_distinct(Xs),
    maplist({Xs, NumCorrect}/[Guess]>>matches(Xs, Guess, NumCorrect), Sets).

matches(Xs, Guess, NumCorrect) :-
    maplist([X, G, B]>>(X #= G #<==> B), Xs, Guess, Bs),
    sum(Bs, #=, NumCorrect).
