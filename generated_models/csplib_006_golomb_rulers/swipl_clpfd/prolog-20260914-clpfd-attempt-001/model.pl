:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Marks, [marks-Marks, length-Last], min(Last)) :-
    Size = Instance.size,
    Longest is Size * Size,
    length(Marks, Size),
    Marks ins 0..Longest,
    Marks = [First|_],
    First #= 0,
    chain(Marks, #<),
    last(Marks, Last),
    findall(I-J, (between(1, Size, I), Next is I + 1, between(Next, Size, J)), Pairs),
    maplist(gap(Marks), Pairs, Differences),
    all_distinct(Differences).

gap(Marks, I-J, Difference) :-
    nth1(I, Marks, Earlier),
    nth1(J, Marks, Later),
    Difference #= Later - Earlier.
