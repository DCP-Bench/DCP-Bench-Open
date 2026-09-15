:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Appointment scheduling: give every person exactly one slot, every slot
% exactly one person, and only where the free-busy matrix allows it.
model(Instance, Vars, [x-Rows]) :-
    M = Instance.m,
    length(M, N),
    length(Rows, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 0..1), Rows),
    append(Rows, Vars),
    % The slot a person takes must be one they are free for.
    maplist([Row, Free]>>scalar_product(Free, Row, #=, 1), Rows, M),
    % One slot per person, and one person per slot.
    maplist([Row]>>sum(Row, #=, 1), Rows),
    transpose(Rows, Columns),
    maplist([Column]>>sum(Column, #=, 1), Columns).
