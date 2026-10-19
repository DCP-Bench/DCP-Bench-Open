% Kakuro (DCP-Bench): fill the white cells of an n x n grid with digits 1..9
% so that each clue's entry sums to the clue and no digit repeats in an entry.
% Black cells (the instance's `blanks`) are output as 0. Coordinates are 1-based.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [x-Rows]) :-
    memberchk(n-N, Instance),
    memberchk(problem-Entries, Instance),
    memberchk(blanks-Black, Instance),
    dim(M, [N, N]),
    flatten_array(M, Vars),

    % Each white cell takes a digit 1..9; each black cell is 0.
    % Digits in white cells: 1..9 (a digit is a non-zero value, so white cells exclude 0).
    M[1..N,1..N] :: 0..9,
    (   multifor([R,C], 1, [N,N]),
        param(Black, M)
    do
        (   memberchk([R,C], Black)
        ->  M[R,C] #= 0
        ;   M[R,C] #>= 1
        )
    ),

    % The sum of the numbers in each entry matches the clue associated with it.
    % No digit is duplicated in any entry.
    (   foreach([Clue|Coords], Entries),
        param(M)
    do
        cells_of(M, Coords, Xs),
        sum(Xs) #= Clue,
        alldifferent(Xs)
    ),

    % Output: the solution matrix as a list of rows.
    (   for(I, 1, N),
        foreach(Row, Rows),
        param(M, N)
    do
        collection_to_list(M[I,1..N], Row)
    ).

cells_of(_, [], []).
cells_of(M, [[R,C]|Cs], [X|Xs]) :-
    X is M[R,C],
    cells_of(M, Cs, Xs).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
