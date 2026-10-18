% N-puzzle (sliding tile puzzle): trace the steps from the start picture to the
% end picture. The puzzle has N_STEPS states, the first is puzzle_start, the last
% is puzzle_end. Each state is a D x D board holding the tiles 0..D*D-1 once each,
% 0 is the empty cell. D is the side of puzzle_start in the instance.
%
% Encoding: the blank is kept as a row and a column variable per state, so the
% adjacency of consecutive blanks is a plain sum of two distances.
%
% Freezing is not allowed: the state must change at each step. Every step moves
% the blank to a neighbouring cell, so the board changes and no step is frozen.

:- lib(ic).
:- lib(lists).
:- lib(listut).

model(Instance, Vars, [steps-States]) :-
    memberchk('N_STEPS'-NS, Instance),
    memberchk(puzzle_start-Start, Instance),
    memberchk(puzzle_end-Goal, Instance),
    length(Start, D),
    NC is D*D - 1,
    % Each state is a board of D x D tiles, and every tile appears once.
    length(States, NS),
    ( foreach(G, States), param(D, NC) do
        length(G, D),
        ( foreach(Row, G), param(D, NC) do
            length(Row, D),
            Row :: 0..NC
        ),
        flatten(G, Flat),
        alldifferent(Flat)
    ),
    % Blank coordinates (1-based row and column) for each state.
    length(Rs, NS), Rs :: 1..D,
    length(Cs, NS), Cs :: 1..D,
    ( foreach(G, States), foreach(R, Rs), foreach(C, Cs), param(D) do
        blank_at(G, D, R, C)
    ),
    % Each step slides one tile into the blank: the blank moves to a neighbouring cell.
    moves(States, Rs, Cs, D, NC),
    % The first state is the puzzle_start, the last state is the puzzle_end.
    States = [First|_],
    append(_, [Last], States),
    fix_grid(First, Start),
    fix_grid(Last, Goal),
    interleave(Rs, Cs, Vars).

% The blank is the 0 tile: the board holds 0 at (R, C) exactly when the blank is at (R, C).
blank_at(G, D, R, C) :-
    ( for(I, 1, D), foreach(Row, G), param(R, C, D) do
        ( for(J, 1, D), foreach(X, Row), param(R, C, I, D) do
            (X #= 0) <=> ((R #= I) and (C #= J))
        )
    ).

% Consecutive boards: the blank moves to a neighbouring cell (one step up, down,
% left or right), the tile on that cell moves into the old blank cell, and every
% other cell keeps its tile.
moves([G0, G1|Gs], [R0, R1|Rs], [C0, C1|Cs], D, NC) :-
    move(G0, G1, R0, C0, R1, C1, D, NC),
    moves([G1|Gs], [R1|Rs], [C1|Cs], D, NC).
moves([_], [_], [_], _, _).

move(G0, G1, R0, C0, R1, C1, D, NC) :-
    abs(R0 - R1) + abs(C0 - C1) #= 1,
    V :: 1..NC,
    ( for(I, 1, D), foreach(Row0, G0), foreach(Row1, G1), param(R0, C0, R1, C1, V, D) do
        ( for(J, 1, D), foreach(X0, Row0), foreach(X1, Row1), param(R0, C0, R1, C1, V, I, D) do
            ( ((R1 #= I) and (C1 #= J)) => (X0 #= V) ),
            ( ((R0 #= I) and (C0 #= J)) => (X1 #= V) ),
            ( (((R0 #\= I) or (C0 #\= J)) and ((R1 #\= I) or (C1 #\= J))) => (X1 #= X0) )
        )
    ).

fix_grid(G, Vals) :-
    ( foreach(Row, G), foreach(VRow, Vals) do
        ( foreach(X, Row), foreach(V, VRow) do
            X #= V
        )
    ).

interleave([], [], []).
interleave([R|Rs], [C|Cs], [R, C|Vs]) :-
    interleave(Rs, Cs, Vs).
