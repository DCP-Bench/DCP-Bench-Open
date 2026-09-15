:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Who killed Agatha: three residents of Dreadsbury Mansion, a web of hatred
% and wealth, and exactly one consistent culprit.
model(Instance, Vars, [killer-Killer]) :-
    Names = Instance.names,
    length(Names, N),
    % The roles are positional in the puzzle statement: the names list runs
    % Agatha, the butler, Charles, and Agatha is the victim.
    Agatha = 1, Butler = 2, Charles = 3,
    Victim = Agatha,
    Top is N - 1,
    Killer in 0..Top,
    square(N, Hates),
    square(N, Richer),
    append(Hates, HatesFlat),
    append(Richer, RicherFlat),
    append([[Killer], HatesFlat, RicherFlat], Vars),

    % A killer always hates, and is no richer than, the victim.  The killer is
    % a variable, so both facts are read off with element/3, which is 1-based
    % while the killer index is 0-based.
    Position #= Killer + 1,
    column(Hates, Victim, HatesVictim),
    column(Richer, Victim, RicherThanVictim),
    element(Position, HatesVictim, 1),
    element(Position, RicherThanVictim, 0),

    % Nobody is richer than himself, and richer is antisymmetric and total.
    numlist(1, N, People),
    maplist({Richer}/[I]>>cell(Richer, I, I, 0), People),
    maplist({Richer, N}/[I]>>antisymmetric(Richer, N, I), People),

    % Charles hates nobody that Agatha hates.
    maplist({Hates, Agatha, Charles}/[I]>>
                (cell(Hates, Agatha, I, A), cell(Hates, Charles, I, C),
                 A #= 1 #==> C #= 0),
            People),

    % Agatha hates everybody except the butler.
    cell(Hates, Agatha, Agatha, 1),
    cell(Hates, Agatha, Charles, 1),
    cell(Hates, Agatha, Butler, 0),

    % The butler hates everyone not richer than Agatha, and everyone Agatha
    % hates.
    maplist({Hates, Richer, Agatha, Butler}/[I]>>
                (cell(Richer, I, Agatha, R), cell(Hates, Butler, I, B),
                 R #= 0 #==> B #= 1),
            People),
    maplist({Hates, Agatha, Butler}/[I]>>
                (cell(Hates, Agatha, I, A), cell(Hates, Butler, I, B),
                 A #= 1 #==> B #= 1),
            People),

    % Nobody hates everyone.
    Most is N - 1,
    maplist({Most}/[Row]>>sum(Row, #=<, Most), Hates).

square(N, Rows) :-
    length(Rows, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 0..1), Rows).

cell(Rows, I, J, Value) :-
    nth1(I, Rows, Row),
    nth1(J, Row, Cell),
    Cell #= Value.

column(Rows, J, Column) :-
    maplist({J}/[Row, Cell]>>nth1(J, Row, Cell), Rows, Column).

antisymmetric(Richer, N, I) :-
    Next is I + 1,
    (   Next > N
    ->  true
    ;   numlist(Next, N, Others),
        maplist({Richer, I}/[J]>>
                    (nth1(I, Richer, RowI), nth1(J, RowI, Forward),
                     nth1(J, Richer, RowJ), nth1(I, RowJ, Backward),
                     Forward #\= Backward),
                Others)
    ).
