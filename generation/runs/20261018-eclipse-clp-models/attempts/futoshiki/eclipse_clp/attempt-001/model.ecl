% Futoshiki puzzle on an N x N grid (N taken from the instance).
% Place the numbers 1 to N so that each row and each column contains each
% digit 1 to N once. Some digits are given; inequality signs between
% neighbouring cells must be honoured. Output: the completed grid.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [grid-Grid], none) :-
    memberchk(values-Values, Instance),
    memberchk(lt-Lt, Instance),
    length(Values, N),
    length(Grid, N),
    ( foreach(XRow, Grid) do
        length(XRow, N),
        XRow :: 1..N
    ),
    flatten(Grid, Vars),

    % Some digits may be given at the start.
    ( foreach(Row, Values), foreach(XRow, Grid) do
        ( foreach(V, Row), foreach(X, XRow) do
            ( V =:= 0 -> true ; X #= V )
        )
    ),

    % The objective is to place the numbers 1 to N such that each row
    % contains each of the digits 1 to N.
    ( foreach(XRow, Grid) do
        alldifferent(XRow)
    ),

    % ... and each column contains each of the digits 1 to N.
    ( for(J, 1, N), param(Grid, N) do
        ( foreach(XRow, Grid), foreach(X, Col), param(J) do
            nth1(J, XRow, X)
        ),
        alldifferent(Col)
    ),

    % Inequality constraints are specified between some of the squares,
    % such that one must be higher or lower than its neighbour.
    % Each entry [R1,C1,R2,C2] (1-based) says cell (R1,C1) < cell (R2,C2).
    ( foreach(Ineq, Lt), param(Grid) do
        Ineq = [R1, C1, R2, C2],
        nth1(R1, Grid, Row1), nth1(C1, Row1, A),
        nth1(R2, Grid, Row2), nth1(C2, Row2, B),
        A #< B
    ).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
