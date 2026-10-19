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
    grid_rows(N, N, Grid),
    flatten(Grid, Vars),

    % Some digits may be given at the start.
    givens(Values, Grid),

    % Each row contains each of the digits 1 to N once.
    all_rows_different(Grid),

    % Each column contains each of the digits 1 to N once.
    all_columns_different(Grid, 1, N),

    % Inequality constraints are specified between some of the squares,
    % such that one must be higher or lower than its neighbour.
    % Each entry [R1,C1,R2,C2] (1-based) says cell (R1,C1) < cell (R2,C2).
    inequalities(Lt, Grid).

grid_rows(0, _, []) :- !.
grid_rows(R, N, [Row|Rows]) :-
    length(Row, N),
    Row :: 1..N,
    R1 is R - 1,
    grid_rows(R1, N, Rows).

givens([], []).
givens([ValRow|ValRows], [GridRow|GridRows]) :-
    givens_row(ValRow, GridRow),
    givens(ValRows, GridRows).

givens_row([], []).
givens_row([V|Vs], [X|Xs]) :-
    ( V =:= 0 -> true ; X #= V ),
    givens_row(Vs, Xs).

all_rows_different([]).
all_rows_different([Row|Rows]) :-
    alldifferent(Row),
    all_rows_different(Rows).

all_columns_different(_, J, N) :- J > N, !.
all_columns_different(Grid, J, N) :-
    column(Grid, J, Col),
    alldifferent(Col),
    J1 is J + 1,
    all_columns_different(Grid, J1, N).

column([], _, []).
column([GridRow|GridRows], J, [X|Xs]) :-
    nth1(J, GridRow, X),
    column(GridRows, J, Xs).

inequalities([], _).
inequalities([[R1, C1, R2, C2]|Ineqs], Grid) :-
    nth1(R1, Grid, Row1), nth1(C1, Row1, A),
    nth1(R2, Grid, Row2), nth1(C2, Row2, B),
    A #< B,
    inequalities(Ineqs, Grid).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
