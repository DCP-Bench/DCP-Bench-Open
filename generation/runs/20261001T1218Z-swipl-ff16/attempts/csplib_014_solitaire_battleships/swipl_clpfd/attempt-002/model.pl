:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Solitaire battleships: fill a grid with a fleet of ships (battleships of 4
% squares, cruisers of 3, destroyers of 2, submarines of 1), horizontal or
% vertical, with no two ships touching, not even at the corners. The row and
% column numbers give how many squares of each are occupied. Every square is
% water, a submarine, or a ship part (left, right, top, bottom or middle).
%
% Each square is kept twice: as a number (its code) and as one 0/1 flag per
% code. The rules about neighbouring squares are written on the flags, as small
% sums of 0/1 values, which the solver propagates much faster than implications
% between several equalities of the codes.
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
    max_list([Water, Circle, Left, Right, Top, Bottom, Middle], MaxCode),
    Codes = c(Water, Circle, Left, Right, Top, Bottom, Middle),

    % Grid[r][c] = the code of the square in row r, column c (both from 0)
    length(Grid, Rows),
    maplist({Cols, MaxCode}/[Row]>>(length(Row, Cols), Row ins 0..MaxCode), Grid),

    % Is[r][c][k] is 1 when the square holds code k
    numlist(0, MaxCode, CodeNumbers),
    maplist({CodeNumbers}/[Row, IsRow]>>maplist({CodeNumbers}/[Cell, Flags]>>
                maplist({Cell}/[Code, Flag]>>(Flag #<==> (Cell #= Code)), CodeNumbers, Flags),
                Row, IsRow),
            Grid, Is),

    % Occupied[r][c] is 1 when the square holds any part of a ship (not water)
    maplist({Water}/[IsRow, OccupiedRow]>>maplist({Water}/[Flags, Occupied]>>
                (nth0(Water, Flags, IsWater), Occupied #= 1 - IsWater),
                IsRow, OccupiedRow),
            Is, Occupied),
    Board = board(Is, Occupied),

    % squares known at the start
    maplist(hint(Grid), Hints),

    % the row and column numbers: occupied squares in each row and column
    maplist([OccupiedRow, Sum]>>sum(OccupiedRow, #=, Sum), Occupied, RowSum),
    transpose(Occupied, OccupiedByColumn),
    maplist([OccupiedColumn, Sum]>>sum(OccupiedColumn, #=, Sum), OccupiedByColumn, ColSum),

    % each square constrains its surroundings: ships do not touch and the parts
    % of a ship fit together
    LastRow is Rows - 1,
    LastCol is Cols - 1,
    findall(R-C, (between(0, LastRow, R), between(0, LastCol, C)), Squares),
    maplist(surroundings(Board, Codes), Squares),

    % the fleet: as many submarines as listed ...
    memberchk([1, Submarines], FleetCounts),
    flags_of_code(Board, Squares, Circle, CircleFlags),
    sum(CircleFlags, #=, Submarines),
    % ... and as many ships of each longer size as listed
    maplist(ships_of_size(Board, Rows, Cols, Codes), FleetCounts),
    % every longer ship has exactly one left or top end, so there is no ship
    % of a size the fleet does not list
    findall(Count, (member([Size, Count], FleetCounts), Size > 1), LongCounts),
    sum_list(LongCounts, LongShips),
    flags_of_code(Board, Squares, Left, LeftFlags),
    flags_of_code(Board, Squares, Top, TopFlags),
    append(LeftFlags, TopFlags, Ends),
    sum(Ends, #=, LongShips),

    % The search first decides which squares are occupied (the row and column
    % numbers act on those flags directly), then what each occupied square
    % holds. The orientation flags of the middle parts follow from the squares.
    append(Occupied, OccupiedFlags),
    append(Grid, Cells),
    append(OccupiedFlags, Cells, Vars).

% The square at the hint holds the given code.
hint(Grid, [R, C, Code]) :-
    nth0(R, Grid, Row),
    nth0(C, Row, Cell),
    Cell #= Code.

% The flags "square (R,C) holds Code" of all the squares.
flags_of_code(Board, Squares, Code, Flags) :-
    maplist({Board, Code}/[R-C, Flag]>>holds(Board, R, C, Code, Flag), Squares, Flags).

% Flag is the 0/1 value "square (R,C) holds Code"; 0 off the grid, where no
% square holds anything.
holds(board(Is, _), R, C, Code, Flag) :-
    (   R >= 0, C >= 0, nth0(R, Is, Row), nth0(C, Row, Flags)
    ->  nth0(Code, Flags, Flag)
    ;   Flag = 0
    ).

% Flag is the 0/1 value "square (R,C) holds some ship part"; 0 off the grid.
occupied(board(_, Occupied), R, C, Flag) :-
    (   R >= 0, C >= 0, nth0(R, Occupied, Row), nth0(C, Row, Flag0)
    ->  Flag = Flag0
    ;   Flag = 0
    ).

% What the square (R,C) requires of its surroundings, depending on what it holds.
surroundings(Board, c(_, Circle, Left, Right, Top, Bottom, Middle), R-C) :-
    Up is R - 1, Down is R + 1, West is C - 1, East is C + 1,
    occupied(Board, R, C, Here),
    occupied(Board, Up, C, UpOccupied),
    occupied(Board, Down, C, DownOccupied),
    occupied(Board, R, West, WestOccupied),
    occupied(Board, R, East, EastOccupied),
    % no ship part touches another ship at a corner
    maplist({Board, Here}/[Row, Col]>>(occupied(Board, Row, Col, Corner), Here + Corner #=< 1),
            [Up, Up, Down, Down], [West, East, West, East]),
    % a submarine is surrounded by water
    holds(Board, R, C, Circle, IsCircle),
    maplist({IsCircle}/[Neighbour]>>(IsCircle + Neighbour #=< 1),
            [UpOccupied, DownOccupied, WestOccupied, EastOccupied]),
    % the left end of a horizontal ship: a middle or right part to its right,
    % water on the other three sides
    holds(Board, R, C, Left, IsLeft),
    holds(Board, R, East, Middle, EastMiddle),
    holds(Board, R, East, Right, EastRight),
    IsLeft #=< EastMiddle + EastRight,
    maplist({IsLeft}/[Neighbour]>>(IsLeft + Neighbour #=< 1),
            [WestOccupied, UpOccupied, DownOccupied]),
    % the right end: a middle or left part to its left, water on the other three
    holds(Board, R, C, Right, IsRight),
    holds(Board, R, West, Middle, WestMiddle),
    holds(Board, R, West, Left, WestLeft),
    IsRight #=< WestMiddle + WestLeft,
    maplist({IsRight}/[Neighbour]>>(IsRight + Neighbour #=< 1),
            [EastOccupied, UpOccupied, DownOccupied]),
    % the top end of a vertical ship: a middle or bottom part below it
    holds(Board, R, C, Top, IsTop),
    holds(Board, Down, C, Middle, DownMiddle),
    holds(Board, Down, C, Bottom, DownBottom),
    IsTop #=< DownMiddle + DownBottom,
    maplist({IsTop}/[Neighbour]>>(IsTop + Neighbour #=< 1),
            [UpOccupied, WestOccupied, EastOccupied]),
    % the bottom end: a middle or top part above it
    holds(Board, R, C, Bottom, IsBottom),
    holds(Board, Up, C, Middle, UpMiddle),
    holds(Board, Up, C, Top, UpTop),
    IsBottom #=< UpMiddle + UpTop,
    maplist({IsBottom}/[Neighbour]>>(IsBottom + Neighbour #=< 1),
            [DownOccupied, WestOccupied, EastOccupied]),
    % a middle part lies in a horizontal ship (a left or middle part to its
    % left, a right or middle part to its right, water above and below) or in a
    % vertical one (a top or middle part above, a bottom or middle part below,
    % water on both sides): Horizontal and Vertical say which, exactly one of
    % them for a middle part and neither otherwise
    holds(Board, R, C, Middle, IsMiddle),
    Horizontal in 0..1,
    Vertical in 0..1,
    IsMiddle #= Horizontal + Vertical,
    holds(Board, R, West, Left, WestLeftPart),
    holds(Board, R, East, Right, EastRightPart),
    Horizontal #=< WestLeftPart + WestMiddle,
    Horizontal #=< EastRightPart + EastMiddle,
    Horizontal + UpOccupied #=< 1,
    Horizontal + DownOccupied #=< 1,
    holds(Board, Up, C, Top, UpTopPart),
    holds(Board, Down, C, Bottom, DownBottomPart),
    Vertical #=< UpTopPart + UpMiddle,
    Vertical #=< DownBottomPart + DownMiddle,
    Vertical + WestOccupied #=< 1,
    Vertical + EastOccupied #=< 1.

% FleetCounts entry [Size, Count]: exactly Count ships of that size lie on the
% grid. A ship of Size squares is an end part, Size-2 middle parts and the other
% end part in a line. Submarines (size 1) are counted separately.
ships_of_size(Board, Rows, Cols, c(_, _, Left, Right, Top, Bottom, Middle), [Size, Count]) :-
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
        maplist(ship_here(Board, Span, Left, Right, Top, Bottom, Middle), Placements, Flags),
        sum(Flags, #=, Count)
    ).

% Flag is 1 when a ship starts at the square (R,C) and extends Span more
% squares, by (DR, DC) per square: first end, middle parts, last end.
ship_here(Board, Span, Left, Right, Top, Bottom, Middle, r(R, C, DR, DC), Flag) :-
    (   DR =:= 0
    ->  FirstCode = Left, LastCode = Right
    ;   FirstCode = Top, LastCode = Bottom
    ),
    EndR is R + DR * Span, EndC is C + DC * Span,
    holds(Board, R, C, FirstCode, First),
    holds(Board, EndR, EndC, LastCode, Last),
    Inner is Span - 1,
    findall(K, between(1, Inner, K), Steps),
    maplist({Board, R, C, DR, DC, Middle}/[K, Part]>>(
                MR is R + DR * K, MC is C + DC * K,
                holds(Board, MR, MC, Middle, Part)),
            Steps, Middles),
    sum([First, Last|Middles], #=, Total),
    Length is Span + 1,
    Flag #<==> (Total #= Length).

% Smallest domain first, ties broken by the most constraints: the squares in the
% rows and columns that are nearly full or empty are settled first.
labeling_options([ffc]).
