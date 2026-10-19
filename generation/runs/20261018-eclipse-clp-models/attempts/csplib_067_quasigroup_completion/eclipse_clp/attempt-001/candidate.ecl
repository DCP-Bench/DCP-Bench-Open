% Quasigroup completion (CSPLib 067): complete a partially filled order N
% quasigroup, an N x N multiplication table over 1..N in which every
% symbol occurs exactly once in every row and every column.
% The instance gives N and the partial table "start", where 0 marks an empty cell.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [puzzle-Rows]) :-
    % order N and the partially filled table come from the instance
    memberchk('N'-N, Instance),
    memberchk(start-Start, Instance),

    % the completed quasigroup: N rows of N cells, each cell a symbol 1..N
    length(Rows, N),
    ( foreach(Row, Rows), param(N) do
        length(Row, N),
        Row :: 1..N
    ),

    % the given cells keep their value; a 0 in the table is an empty cell
    ( foreach(SRow, Start), foreach(Row, Rows) do
        ( foreach(S, SRow), foreach(X, Row) do
            ( S > 0 -> X #= S ; true )
        )
    ),

    % every row contains each symbol exactly once
    ( foreach(Row, Rows) do
        alldifferent(Row)
    ),

    % every column contains each symbol exactly once
    ( for(J, 1, N), param(Rows) do
        ( foreach(Row, Rows), foreach(X, Col), param(J) do
            nth1(J, Row, X)
        ),
        alldifferent(Col)
    ),

    flatten(Rows, Vars).

% first-fail variable order, smallest value first, complete search
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
