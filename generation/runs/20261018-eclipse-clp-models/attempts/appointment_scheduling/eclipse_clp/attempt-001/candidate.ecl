% Appointment scheduling: schedule the people into the interview slots based on
% their free-busy schedules. Print the assignment of people to slots (x) as a
% list of lists of booleans, where x[i][j] is True if person i is assigned to
% slot j, and False otherwise.
% m[i][j] = 1 when person i is free in slot j (busy when 0).

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [x-Rows], none) :-
    memberchk(m-M, Instance),
    length(M, N),
    ( foreach(_, M), foreach(Row, Rows), param(N) do
        length(Row, N)
    ),
    flatten(Rows, Vars),

    % schedule based on their free-busy schedules: a person is assigned only to
    % slots where they are free
    ( foreach(Mrow, M), foreach(Row, Rows) do
        ( foreach(Mij, Mrow), foreach(X, Row) do
            X :: 0..Mij
        )
    ),

    % each person is assigned to exactly one slot
    ( foreach(Row, Rows) do
        sum(Row) #= 1
    ),

    % each slot is assigned to exactly one person
    ( for(J, 1, N), param(Rows) do
        ( foreach(Row, Rows), foreach(X, Col), param(J) do
            nth1(J, Row, X)
        ),
        sum(Col) #= 1
    ).
