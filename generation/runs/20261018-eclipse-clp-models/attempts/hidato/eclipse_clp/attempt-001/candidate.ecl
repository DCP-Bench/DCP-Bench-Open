% Hidato (Hidato puzzles): fill an R x C grid so that the numbers 1..R*C
% appear exactly once each, consecutive numbers touch horizontally,
% vertically or diagonally, and the given numbered tiles stay in place.
% The instance gives the puzzle as a grid, 0 marks an empty cell.
% Output x is the completed grid.
%
% Model: P[k] is the cell (1-based flat index) holding number k. The cell
% is given by its row R[k] and column C[k]. Number k+1 must touch number k.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [x-Grid]) :-
    memberchk(puzzle-Rows, Instance),
    length(Rows, NR),
    Rows = [Row1 | _],
    length(Row1, NC),
    M is NR * NC,
    flatten(Rows, Flat0),
    clue_pairs(Flat0, 1, Clues),

    % Every number 1..M has a cell, and every cell gets a different number.
    length(Ps, M), Ps :: 1..M,
    length(Rs, M), Rs :: 1..NR,
    length(Cs, M), Cs :: 1..NC,
    link_cells(Ps, Rs, Cs, NC),
    alldifferent(Ps),

    % The numbered tiles of the puzzle keep their cells.
    fix_clues(Clues, Ps),

    % The grid itself: cell Flat[p] holds the number k with P[k] = p.
    length(Flat, M), Flat :: 1..M,
    alldifferent(Flat),
    channel(Ps, 1, Flat),

    % Consecutive numbers must touch horizontally, vertically or diagonally.
    adjacency(Rs, Cs),

    chunk(Flat, NC, Grid),
    append(Ps, Rs, PsRs),
    append(PsRs, Cs, Vars).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% Pairs Pos-Value for every numbered tile (non-zero entry).
clue_pairs([], _, []).
clue_pairs([V | Vs], Pos, Clues) :-
    Pos1 is Pos + 1,
    (   V =:= 0
    ->  Clues = Clues1
    ;   Clues = [Pos-V | Clues1]
    ),
    clue_pairs(Vs, Pos1, Clues1).

% A numbered tile with value V sits at position Pos: P[V] = Pos.
fix_clues([], _).
fix_clues([Pos-V | Clues], Ps) :-
    nth1(V, Ps, PV),
    PV #= Pos,
    fix_clues(Clues, Ps).

% Cell index of row R and column C (1-based) is (R-1)*NC + C.
link_cells([], [], [], _).
link_cells([P | Ps], [R | Rs], [C | Cs], NC) :-
    P #= (R - 1) * NC + C,
    link_cells(Ps, Rs, Cs, NC).

% Number K is in cell P[K], so Flat at that cell is K.
channel([], _, _).
channel([P | Ps], K, Flat) :-
    element(P, Flat, K),
    K1 is K + 1,
    channel(Ps, K1, Flat).

% Consecutive numbers touch: rows and columns differ by at most 1.
% The cells differ because the numbers are in different cells.
adjacency([R1 | Rs], [C1 | Cs]) :-
    adjacency_(Rs, Cs, R1, C1).

adjacency_([], [], _, _).
adjacency_([R2 | Rs], [C2 | Cs], R1, C1) :-
    R1 - R2 #=< 1,
    R2 - R1 #=< 1,
    C1 - C2 #=< 1,
    C2 - C1 #=< 1,
    adjacency_(Rs, Cs, R2, C2).

% Split the flat list into rows of NC cells.
chunk([], _, []).
chunk(L, NC, [Row | Rows]) :-
    L = [_ | _],
    length(Row, NC),
    append(Row, Rest, L),
    chunk(Rest, NC, Rows).
