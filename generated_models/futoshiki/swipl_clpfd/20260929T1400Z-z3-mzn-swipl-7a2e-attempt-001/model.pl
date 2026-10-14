:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Futoshiki: fill an n x n grid with 1..n so that every row and column has each
% number once, some cells are given, and the listed "less than" signs between
% neighbouring cells hold.
model(Instance, Vars, [grid-Rows]) :-
    Values = Instance.values,   % given cells; 0 means empty
    Lt = Instance.lt,           % [i1, j1, i2, j2]: cell (i1, j1) must be smaller than cell (i2, j2), 1-based
    length(Values, Size),

    length(Rows, Size),
    maplist({Size}/[Row]>>(length(Row, Size), Row ins 1..Size), Rows),

    % the given numbers are fixed
    maplist([Row, ValueRow]>>maplist(given, Row, ValueRow), Rows, Values),

    % every row holds different numbers
    maplist(all_distinct, Rows),
    % every column holds different numbers
    transpose(Rows, Columns),
    maplist(all_distinct, Columns),

    % each inequality sign: the first cell is smaller than the second (the
    % coordinates in the data start at 1, as nth1 does)
    maplist({Rows}/[[I1, J1, I2, J2]]>>(nth1(I1, Rows, Row1), nth1(J1, Row1, Small),
                                        nth1(I2, Rows, Row2), nth1(J2, Row2, Big),
                                        Small #< Big), Lt),
    append(Rows, Vars).

% an empty cell (0 in the data) is left free; any other value is fixed
given(_, 0) :- !.
given(Cell, Value) :- Cell #= Value.
