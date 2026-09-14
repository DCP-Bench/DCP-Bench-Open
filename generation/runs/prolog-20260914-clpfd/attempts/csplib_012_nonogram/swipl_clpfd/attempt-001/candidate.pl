:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [board-Rows]) :-
    RowRules = Instance.row_rules,
    ColRules = Instance.col_rules,
    length(RowRules, Height),
    length(ColRules, Width),
    length(Rows, Height),
    maplist({Width}/[Row]>>(length(Row, Width), Row ins 0..1), Rows),
    append(Rows, Vars),
    maplist(line, Rows, RowRules),
    transpose(Rows, Columns),
    maplist(line, Columns, ColRules).

line(Line, Rule) :-
    automaton_of(Rule, Arcs, Accepting),
    maplist([State, sink(State)]>>true, Accepting, Sinks),
    automaton(Line, [source(0)|Sinks], Arcs).

% The reference's transition function, arc for arc: each nonzero block may be
% preceded by any number of zeros, runs its exact length of ones, and is
% followed by at least one zero. A zero entry is padding and contributes
% nothing.
automaton_of(Rule, Arcs, Accepting) :-
    blocks(Rule, 0, Prefix, Final),
    append(Prefix, [arc(Final, 0, Final)], Arcs),
    Penultimate is Final - 1,
    include([State]>>(State >= 0), [Penultimate, Final], Accepting).

blocks([], State, [], State).
blocks([0|Rest], State, Arcs, Final) :- !,
    blocks(Rest, State, Arcs, Final).
blocks([Length|Rest], State, Arcs, Final) :-
    Length > 0,
    shaded(Length, State, Block, Ending),
    Next is Ending + 1,
    blocks(Rest, Next, More, Final),
    append([[arc(State, 0, State)], Block, [arc(Ending, 0, Next)], More], Arcs).

shaded(0, State, [], State).
shaded(Length, State, [arc(State, 1, Next)|Rest], Ending) :-
    Length > 0,
    Next is State + 1,
    Left is Length - 1,
    shaded(Left, Next, Rest, Ending).
