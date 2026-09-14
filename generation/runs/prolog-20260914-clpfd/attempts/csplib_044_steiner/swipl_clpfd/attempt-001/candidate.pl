:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [sets-Rows]) :-
    N = Instance.n,
    Count is N * (N - 1) // 6,
    length(Rows, Count),
    maplist({N}/[Row]>>(length(Row, N), Row ins 0..1, sum(Row, #=, 3)), Rows),
    append(Rows, Vars),
    findall(I-J, (between(1, Count, I), Next is I + 1, between(Next, Count, J)), Pairs),
    maplist(overlap(Rows), Pairs).

% Two triples share at most one element.
overlap(Rows, I-J) :-
    nth1(I, Rows, First),
    nth1(J, Rows, Second),
    maplist([A, B, Both]>>(Both #= A * B), First, Second, Shared),
    sum(Shared, #=<, 1).
