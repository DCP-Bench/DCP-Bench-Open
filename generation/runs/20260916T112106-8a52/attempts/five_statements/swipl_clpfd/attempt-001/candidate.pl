:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Five self-referential statements, the i-th claiming that exactly i of them
% are false.
model(_Instance, Statements, [statements-Statements]) :-
    length(Statements, 5),
    Statements ins 0..1,
    maplist([S, F]>>(F #= 1 - S), Statements, Falses),
    sum(Falses, #=, FalseCount),
    numlist(1, 5, Indices),
    maplist({Statements, FalseCount}/[I]>>claim(Statements, FalseCount, I),
            Indices).

% Statement I holds exactly when the number of false statements is I.
claim(Statements, FalseCount, I) :-
    nth1(I, Statements, S),
    S #= 1 #<==> FalseCount #= I.
