% Assignment costs: assign people to tasks at minimum total cost.
% Each task must be assigned to exactly one person, but it is not necessary to
% assign all people to a task. x[i][j] is 1 if task i is assigned to person j.
:- lib(ic).
:- lib(listut).

model(Instance, Vars, [x-Rows], min(Cost)) :-
    memberchk(cost-CostRows, Instance),
    length(CostRows, T),
    CostRows = [FirstRow | _],
    length(FirstRow, P),

    % Decision variables: one 0/1 cell per task and person
    length(Rows, T),
    ( foreach(Row, Rows), param(P) do
        length(Row, P),
        Row :: 0..1
    ),
    flatten(Rows, Vars),

    % Each task must be assigned to exactly one person
    ( foreach(Row, Rows) do
        sum(Row) #= 1
    ),

    % It is not necessary to assign all people to a task, but each person takes at most one task
    ( for(J, 1, P), param(Rows) do
        column_vars(Rows, J, Col),
        sum(Col) #=< 1
    ),

    % Total cost: sum of the cost of each chosen task-person pair
    flatten(CostRows, FlatCost),
    ( foreach(C, FlatCost), foreach(X, Vars), foreach(C*X, Terms) do
        true
    ),
    Cost #= sum(Terms).

% Column J (1-based) of a list of rows
column_vars([], _, []).
column_vars([Row | Rows], J, [V | Vs]) :-
    nth1(J, Row, V),
    column_vars(Rows, J, Vs).
