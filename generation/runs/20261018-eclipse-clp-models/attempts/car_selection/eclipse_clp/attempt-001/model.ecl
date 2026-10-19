% car_selection: assign participants to cars to maximize the total number of
% assignments. Each participant may be interested in a subset of the cars.
% Each participant is assigned to at most one car, and each car to at most
% one participant. assignments[i][j] = 1 when participant i gets car j.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [assignments-Rows], max(Total)) :-
    memberchk(possible_assignments-PA, Instance),
    length(PA, N),
    PA = [FirstRow | _],
    length(FirstRow, M),
    length(Rows, N),
    Vars = Flat,

    % each participant may be assigned only to a car they are interested in
    ( foreach(Row, Rows), foreach(PRow, PA), param(M) do
        length(Row, M),
        Row :: 0..1,
        ( foreach(X, Row), foreach(P, PRow) do
            X #=< P
        )
    ),

    % each participant is assigned to at most one car
    ( foreach(Row, Rows) do
        sum(Row) #=< 1
    ),

    % each car is assigned to at most one participant
    ( for(J, 1, M), param(Rows) do
        ( foreach(Row, Rows), foreach(X, Col), param(J) do
            nth1(J, Row, X)
        ),
        sum(Col) #=< 1
    ),

    flatten(Rows, Flat),
    Total #= sum(Flat).
