% Flow Free: connect the matching colours with pipes on a board, so that every
% cell is covered, each colour forms one pipe joining its two clue cells, and
% pipes do not cross or overlap. Output B is the colour of every cell (1..K),
% K being the number of colours (the largest clue).

:- lib(ic).
:- lib(listut).

model(Instance, Vars, ['B'-Rows]) :-
    memberchk(board-Board, Instance),
    length(Board, R),
    Board = [Row1|_],
    length(Row1, C),
    N is R*C,
    flatten(Board, Clues),
    max_of(Clues, K),
    % every cell takes one colour 1..K; a clue cell keeps its colour
    cell_colours(Clues, K, Bs),
    % distance of every cell from the end of its pipe
    length(Ds, N),
    Ds :: 0..N-1,
    cell_rules(1, N, Clues, Bs, Ds, R, C),
    rows(Bs, C, Rows),
    append(Bs, Ds, Vars).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

max_of([X], X).
max_of([X|Xs], M) :-
    max_of(Xs, M0),
    M is max(X, M0).

cell_colours([], _, []).
cell_colours([V|Vs], K, [B|Bs]) :-
    ( V > 0 -> B = V ; B :: 1..K ),
    cell_colours(Vs, K, Bs).

% Each cell belongs to one pipe. A pipe cell has two neighbours of its colour,
% except the two clue cells of a colour, which are the pipe ends and have one.
% Pipes are connected: every cell other than an end has a neighbour of its
% colour one step closer to the end, and the distance never jumps by more than
% one along the pipe. So no loop floats free of the ends.
cell_rules(P, N, _, _, _, _, _) :-
    P > N, !.
cell_rules(P, N, Clues, Bs, Ds, R, C) :-
    nth1(P, Clues, V),
    nth1(P, Bs, Bp),
    nth1(P, Ds, Dp),
    neighbours(P, R, C, Ns),
    neighbour_rules(Ns, Bp, Dp, Bs, Ds, N, Es, Ps),
    (   V > 0 ->
        % a clue cell is a pipe end: one neighbour of its colour, distance 0
        sum(Es) #= 1,
        Dp #= 0
    ;   % any other cell: two neighbours of its colour, and a predecessor
        sum(Es) #= 2,
        Dp #>= 1,
        sum(Ps) #>= 1
    ),
    P1 is P + 1,
    cell_rules(P1, N, Clues, Bs, Ds, R, C).

% For each neighbour q of cell p: E = (same colour), the distance of p is at
% most one more than that of q when they share a colour, and P = (q is the
% predecessor of p: same colour and exactly one step closer to the end).
neighbour_rules([], _, _, _, _, _, [], []).
neighbour_rules([Q|Qs], Bp, Dp, Bs, Ds, N, [E|Es], [Pq|Ps]) :-
    nth1(Q, Bs, Bq),
    nth1(Q, Ds, Dq),
    E #= (Bp #= Bq),
    Dp #=< Dq + 1 + N*(1 - E),
    Pq :: 0..1,
    F #= (Dq #= Dp - 1),
    Pq #=< E,
    Pq #=< F,
    Pq #>= E + F - 1,
    neighbour_rules(Qs, Bp, Dp, Bs, Ds, N, Es, Ps).

% 1-based indices of the cells next to cell P on an R x C board
neighbours(P, R, C, Ns) :-
    I is (P-1) // C + 1,
    J is (P-1) mod C + 1,
    findall(Q, adjacent(I, J, R, C, Q), Ns).

adjacent(I, J, R, C, Q) :-
    member(DI-DJ, [(-1)-0, 1-0, 0-(-1), 0-1]),
    I2 is I + DI,
    J2 is J + DJ,
    I2 >= 1, I2 =< R,
    J2 >= 1, J2 =< C,
    Q is (I2-1)*C + J2.

rows([], _, []).
rows(Bs, C, [Row|Rows]) :-
    Bs = [_|_],
    length(Row, C),
    append(Row, Rest, Bs),
    rows(Rest, C, Rows).
