% Kidney exchange (session3_kidney_exchange) in ECLiPSe, lib(ic).
% At the hospital n people are on a waiting list for a kidney transplant.
% compatible[i] is the set of people (1-based) to which person i can donate.
% Maximise the number of people that receive a new kidney: anyone who gives
% a kidney must receive one, and no person receives more than one kidney.
% transplants[i][j] = 1 if person i donates to person j, and 0 otherwise.

:- lib(ic).
:- lib(listut).
:- lib(lists).

model(Instance, Vars, [transplants-Rows], Objective) :-
    memberchk(num_people-N, Instance),
    memberchk(compatible-Compat, Instance),

    % transplants[i][j] is a 0/1 variable only where j is in compatible[i]; otherwise 0.
    % A person does not donate to himself.
    ( for(I, 1, N), foreach(Row, Rows), param(N, Compat) do
        nth1(I, Compat, Ci),
        row_vars(I, N, Ci, Row)
    ),
    flatten(Rows, Vars),
    ( for(J, 1, N), foreach(Col, Cols), param(Rows) do
        column(J, Rows, Col)
    ),

    % Each person gives at most one kidney.
    ( foreach(Row, Rows) do
        sum(Row) #=< 1
    ),

    % No person receives more than one kidney.
    ( foreach(Col, Cols) do
        sum(Col) #=< 1
    ),

    % Anyone who gives a kidney must receive one.
    ( for(I, 1, N), param(Rows, Cols) do
        nth1(I, Rows, RowI),
        nth1(I, Cols, ColI),
        sum(RowI) #=< sum(ColI)
    ),

    % Maximise the number of people that receive a kidney.
    Objective = max(sum(Vars)).

% Row I of the transplant matrix: entry J is 0/1 when J is compatible with I.
row_vars(I, N, Ci, Row) :-
    length(Row, N),
    ( foreach(X, Row), for(J, 1, N), param(I, Ci) do
        ( J =:= I ->
            X = 0
        ; memberchk(J, Ci) ->
            X :: 0..1
        ;
            X = 0
        )
    ).

% Column J of the transplant matrix: the donations received by person J.
column(J, Rows, Col) :-
    ( foreach(Row, Rows), foreach(X, Col), param(J) do
        nth1(J, Row, X)
    ).
