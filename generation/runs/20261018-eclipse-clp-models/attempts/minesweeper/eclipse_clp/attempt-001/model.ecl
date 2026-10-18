% Minesweeper: the board is a grid of cells, each a mine or not.
% A numbered cell is opened, so it is not a mine. The number on an opened
% cell is the count of mines among its adjacent cells (the eight neighbours,
% clipped at the board edge). Unopened cells carry -1.
% Output: mines, one 0/1 Boolean per cell (1 = mine), as a list of rows.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [mines-Rows], none) :-
    memberchk(game_data-Data, Instance),
    length(Data, R),
    Data = [FirstRow | _],
    length(FirstRow, C),

    % Each cell of the board is a mine (1) or not (0).
    ( foreach(_, Data), foreach(Row, Rows), param(C) do
        length(Row, C),
        Row :: 0..1
    ),
    flatten(Rows, Vars),

    % Opened cells, the ones showing a number, are not mines.
    % The number on each opened cell is the count of mines around it.
    ( multifor([I, J], 1, [R, C]), param(Data, Rows, R, C) do
        nth1(I, Data, DataRow),
        nth1(J, DataRow, Clue),
        nth1(I, Rows, MineRow),
        nth1(J, MineRow, Mine),
        ( Clue >= 0 ->
            Mine #= 0,
            findall(NI-NJ,
                    ( member(DI, [-1, 0, 1]), member(DJ, [-1, 0, 1]),
                      \+ (DI =:= 0, DJ =:= 0),
                      NI is I + DI, NJ is J + DJ,
                      NI >= 1, NI =< R, NJ >= 1, NJ =< C ),
                    Coords),
            ( foreach(NI-NJ, Coords), foreach(X, Xs), param(Rows) do
                nth1(NI, Rows, NRow),
                nth1(NJ, NRow, X)
            ),
            sum(Xs) #= Clue
        ;
            true
        )
    ).

% Label the cells with the most constrained cell first.
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
