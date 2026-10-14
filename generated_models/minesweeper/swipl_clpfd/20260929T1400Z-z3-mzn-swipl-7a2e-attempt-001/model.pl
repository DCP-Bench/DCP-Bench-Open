:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Minesweeper: from the revealed numbers of a board, decide which of the
% unopened cells hold a mine. An opened cell is safe and shows how many of its
% (up to eight) neighbours are mines.
model(Instance, Vars, [mines-Rows]) :-
    Unopened = Instance.'X',       % the value that marks a cell that is not opened
    Game = Instance.game_data,
    length(Game, NRows),
    Game = [FirstRow|_],
    length(FirstRow, NCols),

    % Rows[r][c] is 1 when cell (r, c) holds a mine
    length(Rows, NRows),
    maplist({NCols}/[Row]>>(length(Row, NCols), Row ins 0..1), Rows),

    % the opened cells with their numbers, as ground (row, column, number) data
    findall(R-C-Number, (nth1(R, Game, GameRow), nth1(C, GameRow, Number), Number \== Unopened), Clues),
    maplist({Rows, NRows, NCols}/[R-C-Number]>>(
                % an opened cell is not a mine
                cell(Rows, R, C, 0),
                % its number is the count of mines among its neighbours
                findall(A-B, (between(-1, 1, DA), between(-1, 1, DB), \+ (DA =:= 0, DB =:= 0),
                              A is R + DA, B is C + DB,
                              A >= 1, A =< NRows, B >= 1, B =< NCols), Around),
                maplist({Rows}/[A-B, Mine]>>cell(Rows, A, B, Mine), Around, Neighbours),
                sum(Neighbours, #=, Number)), Clues),
    append(Rows, Vars).

% cell(+Rows, +R, +C, ?Value): the cell in row R and column C (both counted from 1)
cell(Rows, R, C, Value) :-
    nth1(R, Rows, Row),
    nth1(C, Row, Value).
