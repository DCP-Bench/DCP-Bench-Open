:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Solitaire battleships: fill a grid with a fleet of ships (battleships of 4
% squares, cruisers of 3, destroyers of 2, submarines of 1), horizontal or
% vertical, with no two ships touching, not even at the corners. The row and
% column numbers give how many squares of each are occupied. Every square is
% water, a submarine, or a ship part (left, right, top, bottom or middle).
model(Instance, Vars, [grid-Grid]) :-
    Rows = Instance.rows,
    Cols = Instance.cols,
    RowSum = Instance.rowsum,              % occupied squares in each row
    ColSum = Instance.colsum,              % occupied squares in each column
    FleetCounts = Instance.fleet_counts,   % [ship size, how many ships of it]
    Hints = Instance.hints,                % [row, col, code] squares known at the start
    % the codes a square can hold, as fixed by the instance
    get_dict('WATER', Instance, Water),
    get_dict('CIRCLE', Instance, Circle),  % a submarine
    get_dict('LEFT', Instance, Left),
    get_dict('RIGHT', Instance, Right),
    get_dict('TOP', Instance, Top),
    get_dict('BOTTOM', Instance, Bottom),
    get_dict('MIDDLE', Instance, Middle),
    Codes = c(Water, Circle, Left, Right, Top, Bottom, Middle),
    max_list([Water, Circle, Left, Right, Top, Bottom, Middle], MaxCode),

    % Grid[r][c] = what the square in row r, column c (both from 0) holds
    length(Grid, Rows),
    maplist({Cols, MaxCode}/[Row]>>(length(Row, Cols), Row ins 0..MaxCode), Grid),

    % squares known at the start
    maplist(hint(Grid), Hints),

    % Occupied[r][c] is 1 when the square holds any part of a ship
    maplist({Water}/[Row, OccupiedRow]>>maplist({Water}/[Cell, Flag]>>(Flag #<==> (Cell #> Water)),
                                                Row, OccupiedRow),
            Grid, Occupied),

    % the row and column numbers: occupied squares in each row and column
    maplist([OccupiedRow, Sum]>>sum(OccupiedRow, #=, Sum), Occupied, RowSum),
    transpose(Occupied, OccupiedByColumn),
    maplist([OccupiedColumn, Sum]>>sum(OccupiedColumn, #=, Sum), OccupiedByColumn, ColSum),

    % each square constrains its surroundings: ships do not touch and the parts
    % of a ship fit together
    LastRow is Rows - 1,
    LastCol is Cols - 1,
    findall(R-C, (between(0, LastRow, R), between(0, LastCol, C)), Squares),
    maplist(surroundings(Grid, Codes), Squares),

    % the fleet: as many submarines as listed ...
    append(Grid, Cells),
    memberchk([1, Submarines], FleetCounts),
    count_cells(Cells, Circle, Submarines),
    % ... and as many ships of each longer size as listed
    maplist(ships_of_size(Grid, Rows, Cols, Codes), FleetCounts),
    % every longer ship has exactly one left or top end, so there is no ship
    % of a size the fleet does not list
    findall(Count, (member([Size, Count], FleetCounts), Size > 1), LongCounts),
    sum_list(LongCounts, LongShips),
    count_cells(Cells, Left, LeftEnds),
    count_cells(Cells, Top, TopEnds),
    LeftEnds + TopEnds #= LongShips,
    Vars = Cells.

% The square at the hint holds the given code.
hint(Grid, [R, C, Code]) :-
    nth0(R, Grid, Row),
    nth0(C, Row, Cell),
    Cell #= Code.

% Count is the number of cells holding Code.
count_cells(Cells, Code, Count) :-
    maplist({Code}/[Cell, Flag]>>(Flag #<==> (Cell #= Code)), Cells, Flags),
    sum(Flags, #=, Count).

% The square (R,C) is on the grid.
cell_at(Grid, R, C, Cell) :-
    R >= 0, C >= 0,
    nth0(R, Grid, Row),
    nth0(C, Row, Cell).

% Condition: the square (R,C) holds Code. A square off the grid holds nothing,
% so the condition is false there.
holds(Grid, R, C, Code, Condition) :-
    (   cell_at(Grid, R, C, Cell)
    ->  Condition = (Cell #= Code)
    ;   Condition = (1 #= 0)
    ).

% Condition: the square (R,C) holds one of Codes (false off the grid).
holds_one_of(Grid, R, C, Codes, Condition) :-
    (   cell_at(Grid, R, C, Cell)
    ->  maplist({Cell}/[Code, Equal]>>(Equal = (Cell #= Code)), Codes, Equals),
        disjunction(Equals, Condition)
    ;   Condition = (1 #= 0)
    ).

% Condition: the square (R,C) is water. Off the grid there is nothing to
% avoid, so the condition is true there.
water_or_edge(Grid, R, C, Water, Condition) :-
    (   cell_at(Grid, R, C, Cell)
    ->  Condition = (Cell #= Water)
    ;   Condition = (1 #= 1)
    ).

conjunction([Condition], Condition) :- !.
conjunction([Condition|Rest], Condition #/\ Others) :-
    conjunction(Rest, Others).

disjunction([Condition], Condition) :- !.
disjunction([Condition|Rest], Condition #\/ Others) :-
    disjunction(Rest, Others).

% What the square (R,C) requires of its surroundings, depending on what it holds.
surroundings(Grid, c(Water, Circle, Left, Right, Top, Bottom, Middle), R-C) :-
    nth0(R, Grid, Row),
    nth0(C, Row, Cell),
    Up is R - 1, Down is R + 1, West is C - 1, East is C + 1,
    % no ship part touches another ship at a corner: the existing diagonal
    % neighbours are water
    water_or_edge(Grid, Up, West, Water, NorthWest),
    water_or_edge(Grid, Up, East, Water, NorthEast),
    water_or_edge(Grid, Down, West, Water, SouthWest),
    water_or_edge(Grid, Down, East, Water, SouthEast),
    (Cell #> Water) #==> (NorthWest #/\ NorthEast #/\ SouthWest #/\ SouthEast),
    % the neighbours in each direction are water
    water_or_edge(Grid, Up, C, Water, UpWater),
    water_or_edge(Grid, Down, C, Water, DownWater),
    water_or_edge(Grid, R, West, Water, WestWater),
    water_or_edge(Grid, R, East, Water, EastWater),
    % a submarine is surrounded by water
    (Cell #= Circle) #==> (UpWater #/\ DownWater #/\ WestWater #/\ EastWater),
    % the left end of a horizontal ship: a middle or right part to its right,
    % water on the other three sides
    holds_one_of(Grid, R, East, [Middle, Right], EastPart),
    (Cell #= Left) #==> (EastPart #/\ WestWater #/\ UpWater #/\ DownWater),
    % the right end: a middle or left part to its left, water on the other three
    holds_one_of(Grid, R, West, [Middle, Left], WestPart),
    (Cell #= Right) #==> (WestPart #/\ EastWater #/\ UpWater #/\ DownWater),
    % the top end of a vertical ship: a middle or bottom part below it
    holds_one_of(Grid, Down, C, [Middle, Bottom], DownPart),
    (Cell #= Top) #==> (DownPart #/\ UpWater #/\ WestWater #/\ EastWater),
    % the bottom end: a middle or top part above it
    holds_one_of(Grid, Up, C, [Middle, Top], UpPart),
    (Cell #= Bottom) #==> (UpPart #/\ DownWater #/\ WestWater #/\ EastWater),
    % a middle part lies in a horizontal ship (a left or middle part to its
    % left, a right or middle part to its right, water above and below) or in a
    % vertical one (a top or middle part above, a bottom or middle part below,
    % water on both sides)
    holds_one_of(Grid, R, West, [Left, Middle], LeftPart),
    holds_one_of(Grid, R, East, [Right, Middle], RightPart),
    holds_one_of(Grid, Up, C, [Top, Middle], AbovePart),
    holds_one_of(Grid, Down, C, [Bottom, Middle], BelowPart),
    (Cell #= Middle) #==>
        ((LeftPart #/\ RightPart #/\ UpWater #/\ DownWater)
         #\/ (AbovePart #/\ BelowPart #/\ WestWater #/\ EastWater)).

% FleetCounts entry [Size, Count]: exactly Count ships of that size lie on the
% grid. A ship of Size squares is an end part, Size-2 middle parts and the other
% end part in a line. Submarines (size 1) are counted separately.
ships_of_size(Grid, Rows, Cols, c(_, _, Left, Right, Top, Bottom, Middle), [Size, Count]) :-
    (   Size < 2
    ->  true
    ;   Span is Size - 1,
        LastRow is Rows - 1,
        LastCol is Cols - 1,
        LastHorizontalStart is Cols - Size,
        LastVerticalStart is Rows - Size,
        findall(r(R, C, 0, 1), (between(0, LastRow, R), between(0, LastHorizontalStart, C)),
                Horizontal),
        findall(r(R, C, 1, 0), (between(0, LastVerticalStart, R), between(0, LastCol, C)),
                Vertical),
        append(Horizontal, Vertical, Placements),
        maplist(ship_here(Grid, Span, Left, Right, Top, Bottom, Middle), Placements, Flags),
        sum(Flags, #=, Count)
    ).

% Flag is 1 when a ship starts at the square (R,C) and extends Span more
% squares, by (DR, DC) per square: first end, middle parts, last end.
ship_here(Grid, Span, Left, Right, Top, Bottom, Middle, r(R, C, DR, DC), Flag) :-
    (   DR =:= 0
    ->  FirstCode = Left, LastCode = Right
    ;   FirstCode = Top, LastCode = Bottom
    ),
    EndR is R + DR * Span, EndC is C + DC * Span,
    holds(Grid, R, C, FirstCode, First),
    holds(Grid, EndR, EndC, LastCode, Last),
    Inner is Span - 1,
    % the middle squares; the conditions mention grid cells, so they are built
    % with maplist, not findall (which would copy the cells)
    findall(K, between(1, Inner, K), Steps),
    maplist({Grid, R, C, DR, DC, Middle}/[K, Condition]>>(
                MR is R + DR * K, MC is C + DC * K,
                holds(Grid, MR, MC, Middle, Condition)),
            Steps, Middles),
    conjunction([First, Last|Middles], Ship),
    Flag #<==> Ship.
