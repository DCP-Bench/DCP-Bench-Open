:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Car selection: match participants to cars they are interested in, at most
% one car each and one participant per car, maximizing the matches made.
model(Instance, Vars, [assignments-Rows], max(Matched)) :-
    Possible = Instance.possible_assignments,
    length(Possible, Participants),
    Possible = [FirstRow|_],
    length(FirstRow, Cars),
    length(Rows, Participants),
    maplist({Cars}/[Row]>>(length(Row, Cars), Row ins 0..1), Rows),
    append(Rows, Vars),
    % An assignment is only available where the participant is interested.
    maplist(within_interest, Rows, Possible),
    % At most one car per participant, and one participant per car.
    maplist([Row]>>sum(Row, #=<, 1), Rows),
    transpose(Rows, Columns),
    maplist([Column]>>sum(Column, #=<, 1), Columns),
    sum(Vars, #=, Matched).

within_interest(Row, Allowed) :-
    maplist([A, P]>>(A #=< P), Row, Allowed).
