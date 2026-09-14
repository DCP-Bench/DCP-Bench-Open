:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [grid-Rows]) :-
    get_dict(input_grid, Instance, Given),
    length(Given, N),
    Block is round(sqrt(N)),
    length(Rows, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 1..N), Rows),
    append(Rows, Vars),
    maplist(given, Given, Rows),
    maplist(all_distinct, Rows),
    transpose(Rows, Columns),
    maplist(all_distinct, Columns),
    Last is N - Block,
    findall(I-J, (between(0, Last, I), 0 is I mod Block,
                  between(0, Last, J), 0 is J mod Block), Corners),
    maplist(box(Rows, Block), Corners).

% A zero in the instance means an empty cell.
given(GivenRow, Row) :-
    maplist([Value, Cell]>>(Value =:= 0 -> true ; Cell #= Value), GivenRow, Row).

% The cells are gathered by mapping, not by findall/3: findall copies its
% template, and a copied decision variable carries no constraint back.
box(Rows, Block, I-J) :-
    Top is I + 1, Bottom is I + Block,
    LeftEdge is J + 1, RightEdge is J + Block,
    numlist(Top, Bottom, BoxRows),
    numlist(LeftEdge, RightEdge, BoxColumns),
    maplist({Rows, BoxColumns}/[R, Cells]>>box_row(Rows, BoxColumns, R, Cells),
            BoxRows, Lines),
    append(Lines, Cells),
    all_distinct(Cells).

box_row(Rows, BoxColumns, R, Cells) :-
    nth1(R, Rows, Row),
    maplist({Row}/[C, Cell]>>nth1(C, Row, Cell), BoxColumns, Cells).
