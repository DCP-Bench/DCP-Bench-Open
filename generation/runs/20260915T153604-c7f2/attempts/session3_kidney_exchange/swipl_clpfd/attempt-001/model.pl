:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Kidney exchange: pair donors with compatible recipients so that anyone who
% gives also receives, nobody gives or receives twice, and as many transplants
% happen as possible.
model(Instance, Vars, [transplants-Rows], max(Done)) :-
    NumPeople = Instance.num_people,
    % compatible is ragged: one 1-based recipient list per donor.
    Compatible = Instance.compatible,
    length(Rows, NumPeople),
    maplist({NumPeople}/[Row]>>(length(Row, NumPeople), Row ins 0..1), Rows),
    append(Rows, Vars),
    numlist(1, NumPeople, People),
    maplist(only_compatible(People), Rows, Compatible),
    transpose(Rows, Columns),
    maplist(at_most_one, Rows),
    maplist(at_most_one, Columns),
    % Anyone who gives a kidney must also receive one.  With both sums capped
    % at one, that is exactly gives =< receives.
    maplist(give_implies_receive, Rows, Columns),
    sum(Vars, #=, Done).

only_compatible(People, Row, Allowed) :-
    maplist({Allowed}/[Cell, Recipient]>>
                (memberchk(Recipient, Allowed) -> true ; Cell #= 0),
            Row, People).

at_most_one(Cells) :- sum(Cells, #=<, 1).

give_implies_receive(Row, Column) :-
    sum(Row, #=, Gives),
    sum(Column, #=, Receives),
    Gives #=< Receives.
