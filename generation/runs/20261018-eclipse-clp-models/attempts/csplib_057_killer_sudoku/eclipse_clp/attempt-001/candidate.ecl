% Killer sudoku: fill the n x n grid with 1..n so that every row, every column
% and every 3x3 nonet contains each digit exactly once, and each cage's cells
% sum to the number printed in its corner.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [x-Grid], none) :-
    memberchk(n-N, Instance),
    memberchk(problem-Cages, Instance),
    length(Grid, N),
    ( foreach(Row, Grid), param(N) do
        length(Row, N),
        Row :: 1..N
    ),
    flatten(Grid, Vars),

    % Each row contains each number exactly once.
    % Each column contains each number exactly once.
    ( for(R, 1, N), param(N, Grid) do
        findall([R, C], dig_range(1, N, C), RowCoords),
        cells_of(Grid, RowCoords, RowVars),
        alldifferent(RowVars)
    ),
    ( for(C, 1, N), param(N, Grid) do
        findall([R, C], dig_range(1, N, R), ColCoords),
        cells_of(Grid, ColCoords, ColVars),
        alldifferent(ColVars)
    ),

    % Each 3x3 nonet contains each number exactly once.
    ( for(BR, 0, 2), param(Grid) do
        ( for(BC, 0, 2), param(Grid, BR) do
            findall([R, C],
                    ( dig_range(1, 3, DR), dig_range(1, 3, DC),
                      R is 3 * BR + DR, C is 3 * BC + DC ),
                    NonetCoords),
            cells_of(Grid, NonetCoords, NonetVars),
            alldifferent(NonetVars)
        )
    ),

    % The sum of all numbers in a cage must match the small number printed in
    % its corner. No number appears more than once in a cage.
    ( foreach([Sum, CageCoords], Cages), param(Grid) do
        cells_of(Grid, CageCoords, CageVars),
        sum(CageVars) #= Sum,
        alldifferent(CageVars)
    ).

% Integers From..To in order (between/3 is not a builtin in ECLiPSe).
dig_range(From, To, From) :- From =< To.
dig_range(From, To, X) :- From < To, From1 is From + 1, dig_range(From1, To, X).

% The grid cells at the given 1-based [Row, Col] coordinates, in order.
cells_of(Grid, Coords, Vars) :-
    ( foreach([R, C], Coords), foreach(V, Vars), param(Grid) do
        nth1(R, Grid, Row),
        nth1(C, Row, V)
    ).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
