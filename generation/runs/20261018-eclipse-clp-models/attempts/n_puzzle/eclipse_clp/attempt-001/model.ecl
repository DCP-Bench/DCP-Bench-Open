% N-puzzle (sliding tile puzzle). Find N_STEPS board states; the first is the
% puzzle_start, the last is the puzzle_end. A board is D x D, D taken from the data,
% holding the tiles 0..D*D-1 once each, with 0 as the blank.
%
% Each step moves the blank to a neighbouring cell (one cell up, down, left or right)
% and the tile on that cell slides into the blank's old cell.
%
% Freezing is not allowed: the state changes at each step. A blank move always
% changes the board, so the adjacency constraint already gives this.

:- lib(ic).
:- lib(lists).
:- lib(listut).

model(Instance, Vars, [steps-States]) :-
    memberchk('N_STEPS'-NS, Instance),
    memberchk(puzzle_start-Start, Instance),
    memberchk(puzzle_end-Goal, Instance),
    length(Start, D),
    NC is D*D - 1,
    % Board states: each board holds the tiles 0..NC, each exactly once.
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
    % Consecutive states differ by one blank move.
    moves(States, Rs, Cs, D, NC),
    % The first state is the start, the last state is the goal.
    States = [First|_],
    append(_, [Last], States),
    fix_grid(First, Start),
    fix_grid(Last, Goal),
    interleave(Rs, Cs, Vars).

% The blank is at (R, C) exactly when the board holds 0 at that cell.
blank_at(G, D, R, C) :-
    ( for(I, 1, D), foreach(Row, G), param(R, C, D) do
        ( for(J, 1, D), foreach(X, Row), param(R, C, I, D) do
            (X #= 0) <=> ((R #= I) and (C #= J))
        )
    ).

% Consecutive boards: the blank moves to a neighbouring cell, the tile on that
% cell moves into the old blank cell, every other cell stays.
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
